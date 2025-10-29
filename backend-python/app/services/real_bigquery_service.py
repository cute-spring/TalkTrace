"""真实BigQuery服务实现"""
import asyncio
from typing import List, Dict, Any, Optional, AsyncIterator
from datetime import datetime
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd

from app.services.bigquery_service import (
    BigQueryService,
    ConversationRow,
    RetrievalChunkRow,
    ConversationQueryRequest,
    RetrievalChunkQueryRequest
)
from app.utils.logger import logger

class RealBigQueryService(BigQueryService):
    """真实BigQuery服务实现"""

    def __init__(self, project_id: str, dataset_id: str, table_id: str, credentials_path: Optional[str] = None):
        """
        初始化真实BigQuery服务

        Args:
            project_id: GCP项目ID
            dataset_id: BigQuery数据集ID
            table_id: BigQuery表ID
            credentials_path: 服务账号凭证文件路径，为None时使用应用默认凭证
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.conversations_table = f"{project_id}.{dataset_id}.{table_id}"
        self.retrieval_chunks_table = f"{project_id}.{dataset_id}.retrieval_chunks"

        # 初始化BigQuery客户端
        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            self.client = bigquery.Client(project=project_id, credentials=credentials)
        else:
            self.client = bigquery.Client(project=project_id)

        logger.info(
            "RealBigQueryService initialized",
            project_id=project_id,
            dataset_id=dataset_id,
            conversations_table=self.conversations_table,
            retrieval_chunks_table=self.retrieval_chunks_table
        )

    async def test_connection(self) -> bool:
        """测试连接状态"""
        try:
            # 执行简单查询测试连接
            query = f"SELECT 1 as test FROM `{self.conversations_table}` LIMIT 1"
            query_job = self.client.query(query)
            results = list(query_job.result(timeout=10))

            logger.info("BigQuery connection test successful")
            return True
        except Exception as e:
            logger.error("BigQuery connection test failed", error=str(e))
            return False

    async def query_conversations(self, request: ConversationQueryRequest) -> List[ConversationRow]:
        """查询对话记录"""
        logger.info("Querying conversations from BigQuery", request=request.dict())

        # 构建SQL查询
        query = self._build_conversations_query(request)

        try:
            # 执行查询
            query_job = self.client.query(query)
            results = query_job.result(timeout=30)

            # 转换结果
            conversations = []
            for row in results:
                # 解析retrieval_chunk_ids（假设存储为JSON字符串）
                retrieval_chunk_ids = row.get("retrieval_chunk_ids", [])
                if isinstance(retrieval_chunk_ids, str):
                    import json
                    try:
                        retrieval_chunk_ids = json.loads(retrieval_chunk_ids)
                    except json.JSONDecodeError:
                        retrieval_chunk_ids = []

                conversation = ConversationRow(
                    conversation_id=row["conversation_id"],
                    session_id=row["session_id"],
                    message_id=row["message_id"],
                    message_type=row["message_type"],
                    content=row["content"],
                    model_id=row["model_id"],
                    timestamp=row["timestamp"],
                    metadata=dict(row.get("metadata", {})),
                    user_rating=row.get("user_rating"),
                    feedback_text=row.get("feedback_text"),
                    token_count=row.get("token_count"),
                    processing_time_ms=row.get("processing_time_ms"),
                    retrieval_chunk_ids=retrieval_chunk_ids
                )
                conversations.append(conversation)

            logger.info("BigQuery conversation query completed", results_count=len(conversations))
            return conversations

        except Exception as e:
            logger.error("BigQuery conversation query failed", error=str(e), query=query)
            raise

    def _build_conversations_query(self, request: ConversationQueryRequest) -> str:
        """构建对话查询SQL"""
        conditions = []
        params = {}

        # 基础查询
        query = f"""
        SELECT
            conversation_id,
            session_id,
            message_id,
            message_type,
            content,
            model_id,
            timestamp,
            metadata,
            user_rating,
            feedback_text,
            token_count,
            processing_time_ms,
            retrieval_chunk_ids
        FROM `{self.conversations_table}`
        WHERE 1=1
        """

        # 时间范围过滤
        if request.start_time:
            conditions.append("timestamp >= @start_time")
            params["start_time"] = request.start_time

        if request.end_time:
            conditions.append("timestamp <= @end_time")
            params["end_time"] = request.end_time

        # 模型过滤
        if request.model_ids:
            conditions.append("model_id IN UNNEST(@model_ids)")
            params["model_ids"] = request.model_ids

        # 会话过滤
        if request.session_ids:
            conditions.append("session_id IN UNNEST(@session_ids)")
            params["session_ids"] = request.session_ids

        # 消息类型过滤
        if request.message_types:
            conditions.append("message_type IN UNNEST(@message_types)")
            params["message_types"] = request.message_types

        # 关键词搜索
        if request.keywords and request.keywords.strip():
            conditions.append("LOWER(content) LIKE LOWER(@keywords)")
            params["keywords"] = f"%{request.keywords}%"

        # 评分过滤
        if request.min_rating is not None:
            conditions.append("user_rating >= @min_rating")
            params["min_rating"] = request.min_rating

        if request.max_rating is not None:
            conditions.append("user_rating <= @max_rating")
            params["max_rating"] = request.max_rating

        # 添加条件到查询
        if conditions:
            query += " AND " + " AND ".join(conditions)

        # 排序
        order_direction = "ASC" if request.order_direction == "asc" else "DESC"
        query += f" ORDER BY {request.order_by} {order_direction}"

        # 分页
        query += f" LIMIT {request.limit} OFFSET {request.offset}"

        return query

    async def count_conversations(self, request: ConversationQueryRequest) -> int:
        """统计对话记录数量"""
        logger.info("Counting conversations from BigQuery")

        # 构建计数查询
        query = f"""
        SELECT COUNT(*) as total_count
        FROM `{self.conversations_table}`
        WHERE 1=1
        """

        conditions = []
        params = {}

        # 添加相同的过滤条件（不包括排序和分页）
        if request.start_time:
            conditions.append("timestamp >= @start_time")
            params["start_time"] = request.start_time

        if request.end_time:
            conditions.append("timestamp <= @end_time")
            params["end_time"] = request.end_time

        if request.model_ids:
            conditions.append("model_id IN UNNEST(@model_ids)")
            params["model_ids"] = request.model_ids

        if request.session_ids:
            conditions.append("session_id IN UNNEST(@session_ids)")
            params["session_ids"] = request.session_ids

        if request.message_types:
            conditions.append("message_type IN UNNEST(@message_types)")
            params["message_types"] = request.message_types

        if request.keywords and request.keywords.strip():
            conditions.append("LOWER(content) LIKE LOWER(@keywords)")
            params["keywords"] = f"%{request.keywords}%"

        if request.min_rating is not None:
            conditions.append("user_rating >= @min_rating")
            params["min_rating"] = request.min_rating

        if request.max_rating is not None:
            conditions.append("user_rating <= @max_rating")
            params["max_rating"] = request.max_rating

        if conditions:
            query += " AND " + " AND ".join(conditions)

        try:
            query_job = self.client.query(query)
            results = list(query_job.result(timeout=30))

            total_count = results[0]["total_count"] if results else 0
            logger.info("Conversation count completed", total_count=total_count)

            return total_count

        except Exception as e:
            logger.error("Conversation count failed", error=str(e), query=query)
            raise

    async def get_conversation_by_id(self, conversation_id: str) -> Optional[ConversationRow]:
        """根据ID获取对话记录"""
        query = f"""
        SELECT *
        FROM `{self.conversations_table}`
        WHERE conversation_id = @conversation_id
        LIMIT 1
        """

        try:
            query_job = self.client.query(query)
            results = list(query_job.result(timeout=10))

            if not results:
                return None

            row = results[0]
            return ConversationRow(
                conversation_id=row["conversation_id"],
                session_id=row["session_id"],
                message_id=row["message_id"],
                message_type=row["message_type"],
                content=row["content"],
                model_id=row["model_id"],
                timestamp=row["timestamp"],
                metadata=dict(row.get("metadata", {})),
                user_rating=row.get("user_rating"),
                feedback_text=row.get("feedback_text"),
                token_count=row.get("token_count"),
                processing_time_ms=row.get("processing_time_ms"),
                retrieval_chunk_ids=list(row.get("retrieval_chunk_ids", []))
            )

        except Exception as e:
            logger.error("Get conversation by ID failed", error=str(e), conversation_id=conversation_id)
            raise

    async def get_session_conversations(self, session_id: str) -> List[ConversationRow]:
        """获取会话的所有对话"""
        query = f"""
        SELECT *
        FROM `{self.conversations_table}`
        WHERE session_id = @session_id
        ORDER BY timestamp ASC
        """

        try:
            query_job = self.client.query(query)
            results = query_job.result(timeout=30)

            conversations = []
            for row in results:
                conversation = ConversationRow(
                    conversation_id=row["conversation_id"],
                    session_id=row["session_id"],
                    message_id=row["message_id"],
                    message_type=row["message_type"],
                    content=row["content"],
                    model_id=row["model_id"],
                    timestamp=row["timestamp"],
                    metadata=dict(row.get("metadata", {})),
                    user_rating=row.get("user_rating"),
                    feedback_text=row.get("feedback_text"),
                    token_count=row.get("token_count"),
                    processing_time_ms=row.get("processing_time_ms"),
                    retrieval_chunk_ids=list(row.get("retrieval_chunk_ids", []))
                )
                conversations.append(conversation)

            return conversations

        except Exception as e:
            logger.error("Get session conversations failed", error=str(e), session_id=session_id)
            raise

    async def query_retrieval_chunks(self, request: RetrievalChunkQueryRequest) -> List[RetrievalChunkRow]:
        """查询检索片段"""
        logger.info("Querying retrieval chunks from BigQuery", request=request.dict())

        # 构建查询
        query = f"""
        SELECT *
        FROM `{self.retrieval_chunks_table}`
        WHERE 1=1
        """

        conditions = []
        params = {}

        # 文档过滤
        if request.document_ids:
            conditions.append("document_id IN UNNEST(@document_ids)")
            params["document_ids"] = request.document_ids

        # 关键词搜索
        if request.keywords and request.keywords.strip():
            conditions.append("""
                (LOWER(content) LIKE LOWER(@keywords) OR
                 LOWER(title) LIKE LOWER(@keywords))
            """)
            params["keywords"] = f"%{request.keywords}%"

        # 相似度过滤
        if request.min_similarity is not None:
            conditions.append("similarity_score >= @min_similarity")
            params["min_similarity"] = request.min_similarity

        if request.max_similarity is not None:
            conditions.append("similarity_score <= @max_similarity")
            params["max_similarity"] = request.max_similarity

        # 添加条件
        if conditions:
            query += " AND " + " AND ".join(conditions)

        # 排序
        order_direction = "ASC" if request.order_direction == "asc" else "DESC"
        query += f" ORDER BY {request.order_by} {order_direction}"

        # 分页
        query += f" LIMIT {request.limit} OFFSET {request.offset}"

        try:
            query_job = self.client.query(query)
            results = query_job.result(timeout=30)

            chunks = []
            for row in results:
                chunk = RetrievalChunkRow(
                    chunk_id=row["chunk_id"],
                    document_id=row["document_id"],
                    chunk_index=row["chunk_index"],
                    content=row["content"],
                    title=row.get("title"),
                    embedding_vector=list(row.get("embedding_vector", [])),
                    similarity_score=row.get("similarity_score"),
                    metadata=dict(row.get("metadata", {})),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
                chunks.append(chunk)

            logger.info("Retrieval chunks query completed", results_count=len(chunks))
            return chunks

        except Exception as e:
            logger.error("Retrieval chunks query failed", error=str(e), query=query)
            raise

    async def count_retrieval_chunks(self, request: RetrievalChunkQueryRequest) -> int:
        """统计检索片段数量"""
        query = f"""
        SELECT COUNT(*) as total_count
        FROM `{self.retrieval_chunks_table}`
        WHERE 1=1
        """

        conditions = []
        params = {}

        # 添加过滤条件
        if request.document_ids:
            conditions.append("document_id IN UNNEST(@document_ids)")
            params["document_ids"] = request.document_ids

        if request.keywords and request.keywords.strip():
            conditions.append("""
                (LOWER(content) LIKE LOWER(@keywords) OR
                 LOWER(title) LIKE LOWER(@keywords))
            """)
            params["keywords"] = f"%{request.keywords}%"

        if request.min_similarity is not None:
            conditions.append("similarity_score >= @min_similarity")
            params["min_similarity"] = request.min_similarity

        if request.max_similarity is not None:
            conditions.append("similarity_score <= @max_similarity")
            params["max_similarity"] = request.max_similarity

        if conditions:
            query += " AND " + " AND ".join(conditions)

        try:
            query_job = self.client.query(query)
            results = list(query_job.result(timeout=10))

            total_count = results[0]["total_count"] if results else 0
            return total_count

        except Exception as e:
            logger.error("Retrieval chunks count failed", error=str(e), query=query)
            raise

    async def get_chunk_by_id(self, chunk_id: str) -> Optional[RetrievalChunkRow]:
        """根据ID获取检索片段"""
        query = f"""
        SELECT *
        FROM `{self.retrieval_chunks_table}`
        WHERE chunk_id = @chunk_id
        LIMIT 1
        """

        try:
            query_job = self.client.query(query)
            results = list(query_job.result(timeout=10))

            if not results:
                return None

            row = results[0]
            return RetrievalChunkRow(
                chunk_id=row["chunk_id"],
                document_id=row["document_id"],
                chunk_index=row["chunk_index"],
                content=row["content"],
                title=row.get("title"),
                embedding_vector=list(row.get("embedding_vector", [])),
                similarity_score=row.get("similarity_score"),
                metadata=dict(row.get("metadata", {})),
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )

        except Exception as e:
            logger.error("Get chunk by ID failed", error=str(e), chunk_id=chunk_id)
            raise

    async def get_chunks_by_ids(self, chunk_ids: List[str]) -> List[RetrievalChunkRow]:
        """根据ID列表批量获取检索片段"""
        query = f"""
        SELECT *
        FROM `{self.retrieval_chunks_table}`
        WHERE chunk_id IN UNNEST(@chunk_ids)
        """

        try:
            query_job = self.client.query(query)
            results = query_job.result(timeout=30)

            chunks = []
            for row in results:
                chunk = RetrievalChunkRow(
                    chunk_id=row["chunk_id"],
                    document_id=row["document_id"],
                    chunk_index=row["chunk_index"],
                    content=row["content"],
                    title=row.get("title"),
                    embedding_vector=list(row.get("embedding_vector", [])),
                    similarity_score=row.get("similarity_score"),
                    metadata=dict(row.get("metadata", {})),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
                chunks.append(chunk)

            return chunks

        except Exception as e:
            logger.error("Get chunks by IDs failed", error=str(e), chunk_ids=chunk_ids)
            raise

    async def get_available_model_ids(self) -> List[str]:
        """获取所有可用的模型ID"""
        query = f"""
        SELECT DISTINCT model_id
        FROM `{self.conversations_table}`
        WHERE model_id IS NOT NULL
        ORDER BY model_id
        """

        try:
            query_job = self.client.query(query)
            results = query_job.result(timeout=10)

            model_ids = [row["model_id"] for row in results]
            return model_ids

        except Exception as e:
            logger.error("Get available model IDs failed", error=str(e))
            raise

    async def get_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """获取会话统计信息"""
        query = f"""
        SELECT
            COUNT(*) as total_messages,
            COUNTIF(message_type = 'user') as user_messages,
            COUNTIF(message_type = 'assistant') as ai_messages,
            AVG(user_rating) as average_rating,
            ARRAY_AGG(DISTINCT model_id) as models_used,
            SUM(COALESCE(token_count, 0)) as total_tokens,
            SUM(COALESCE(processing_time_ms, 0)) as total_processing_time_ms,
            MIN(timestamp) as first_message_time,
            MAX(timestamp) as last_message_time
        FROM `{self.conversations_table}`
        WHERE session_id = @session_id
        """

        try:
            query_job = self.client.query(query)
            results = list(query_job.result(timeout=10))

            if not results:
                return {}

            row = results[0]

            return {
                "session_id": session_id,
                "total_messages": row["total_messages"],
                "user_messages": row["user_messages"],
                "ai_messages": row["ai_messages"],
                "average_rating": float(row["average_rating"]) if row["average_rating"] else None,
                "models_used": list(row["models_used"] or []),
                "total_tokens": row["total_tokens"],
                "total_processing_time_ms": row["total_processing_time_ms"],
                "first_message_time": row["first_message_time"],
                "last_message_time": row["last_message_time"]
            }

        except Exception as e:
            logger.error("Get session statistics failed", error=str(e), session_id=session_id)
            raise

    async def stream_conversations(self, request: ConversationQueryRequest) -> AsyncIterator[ConversationRow]:
        """流式查询对话记录"""
        logger.info("Streaming conversations from BigQuery")

        # 构建查询
        query = self._build_conversations_query(request)

        try:
            # 使用BigQuery的流式API
            query_job = self.client.query(query)

            for row in query_job.result(timeout=60):
                retrieval_chunk_ids = row.get("retrieval_chunk_ids", [])
                if isinstance(retrieval_chunk_ids, str):
                    import json
                    try:
                        retrieval_chunk_ids = json.loads(retrieval_chunk_ids)
                    except json.JSONDecodeError:
                        retrieval_chunk_ids = []

                conversation = ConversationRow(
                    conversation_id=row["conversation_id"],
                    session_id=row["session_id"],
                    message_id=row["message_id"],
                    message_type=row["message_type"],
                    content=row["content"],
                    model_id=row["model_id"],
                    timestamp=row["timestamp"],
                    metadata=dict(row.get("metadata", {})),
                    user_rating=row.get("user_rating"),
                    feedback_text=row.get("feedback_text"),
                    token_count=row.get("token_count"),
                    processing_time_ms=row.get("processing_time_ms"),
                    retrieval_chunk_ids=retrieval_chunk_ids
                )

                yield conversation

        except Exception as e:
            logger.error("Stream conversations failed", error=str(e), query=query)
            raise