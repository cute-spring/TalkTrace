"""历史记录服务"""
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.history import HistoryRecord, HistorySearchRequest, SessionDetail
from app.services.demo_data import MOCK_HISTORY_DATA, AVAILABLE_MODELS, generate_more_history_data
from app.services.bigquery_factory import get_bigquery_service
from app.services.bigquery_service import ConversationQueryRequest
from app.utils.logger import logger

class HistoryService:
    """历史记录服务类"""

    def __init__(self):
        """初始化历史记录服务"""
        # 获取BigQuery服务实例
        self.bigquery_service = get_bigquery_service()

        # 保留原有的演示数据作为后备（向后兼容）
        base_data = MOCK_HISTORY_DATA + generate_more_history_data(15)
        self.df = pd.DataFrame(base_data)
        self.df['created_at'] = pd.to_datetime(self.df['created_at'], utc=True)

        logger.info("HistoryService initialized with BigQuery integration",
                   service_type=type(self.bigquery_service).__name__,
                   demo_records_count=len(self.df))

    async def search_history(self, request: HistorySearchRequest) -> Dict[str, Any]:
        """搜索历史记录"""
        logger.info("Searching history",
                   start_time=request.start_time,
                   end_time=request.end_time,
                   model_ids=request.model_ids,
                   keywords=request.keywords)

        try:
            # 使用BigQuery服务查询
            bq_request = ConversationQueryRequest(
                start_time=request.start_time,
                end_time=request.end_time,
                model_ids=request.model_ids,
                keywords=request.keywords,
                min_rating=request.rating_range[0] if request.rating_range else None,
                max_rating=request.rating_range[1] if request.rating_range else None,
                limit=request.page_size,
                offset=(request.page - 1) * request.page_size,
                order_by="timestamp",
                order_direction="desc"
            )

            # 查询对话记录
            conversations = await self.bigquery_service.query_conversations(bq_request)

            # 获取总数
            count_request = bq_request.copy()
            count_request.offset = 0
            count_request.limit = 1000000
            total = await self.bigquery_service.count_conversations(count_request)

            # 按会话分组并转换格式
            session_dict = {}
            for conv in conversations:
                if conv.session_id not in session_dict:
                    session_dict[conv.session_id] = {
                        "session_id": conv.session_id,
                        "user_query": "",
                        "ai_response": "",
                        "user_rating": None,
                        "model_id": conv.model_id,
                        "created_at": conv.timestamp,
                        "retrieval_chunks": [],
                        "test_config": None
                    }

                session = session_dict[conv.session_id]
                if conv.message_type == "user":
                    session["user_query"] = conv.content
                elif conv.message_type == "assistant":
                    session["ai_response"] = conv.content
                    session["user_rating"] = conv.user_rating
                    # 获取检索片段
                    if conv.retrieval_chunk_ids:
                        chunks = await self.bigquery_service.get_chunks_by_ids(conv.retrieval_chunk_ids)
                        session["retrieval_chunks"] = [
                            {
                                "id": chunk.chunk_id,
                                "title": chunk.title,
                                "content": chunk.content
                            }
                            for chunk in chunks
                        ]

            # 转换为列表并保持排序
            items = list(session_dict.values())
            items.sort(key=lambda x: x["created_at"], reverse=True)

            result = {
                "items": items,
                "total": total,
                "page": request.page,
                "page_size": request.page_size,
                "total_pages": (total + request.page_size - 1) // request.page_size
            }

            logger.info("History search completed via BigQuery",
                       total_results=total,
                       page=request.page,
                       items_returned=len(items))

            return result

        except Exception as e:
            logger.warning("BigQuery search failed, falling back to demo data", error=str(e))

            # 回退到原有的演示数据逻辑
            return await self._search_demo_data(request)

    async def _search_demo_data(self, request: HistorySearchRequest) -> Dict[str, Any]:
        """使用演示数据进行搜索（回退方案）"""
        logger.info("Using demo data for history search")

        # 复制DataFrame进行过滤
        filtered_df = self.df.copy()

        # 时间范围过滤
        start_dt = pd.to_datetime(request.start_time)
        end_dt = pd.to_datetime(request.end_time)

        mask = (filtered_df['created_at'] >= start_dt) & (filtered_df['created_at'] <= end_dt)
        filtered_df = filtered_df[mask]

        # 模型过滤
        if request.model_ids:
            filtered_df = filtered_df[filtered_df['model_id'].isin(request.model_ids)]

        # 评分范围过滤
        if request.rating_range and len(request.rating_range) == 2:
            min_rating, max_rating = request.rating_range
            filtered_df = filtered_df[
                (filtered_df['user_rating'] >= min_rating) &
                (filtered_df['user_rating'] <= max_rating)
            ]

        # 关键词搜索
        if request.keywords and request.keywords.strip():
            keywords = request.keywords.lower().strip()
            keyword_mask = (
                filtered_df['user_query'].str.lower().str.contains(keywords, na=False) |
                filtered_df['ai_response'].str.lower().str.contains(keywords, na=False)
            )
            filtered_df = filtered_df[keyword_mask]

        # 按时间倒序排序
        filtered_df = filtered_df.sort_values('created_at', ascending=False)

        # 分页
        total = len(filtered_df)
        start_idx = (request.page - 1) * request.page_size
        end_idx = start_idx + request.page_size
        page_data = filtered_df.iloc[start_idx:end_idx]

        # 转换为字典格式
        items = []
        for _, row in page_data.iterrows():
            items.append({
                "session_id": row["session_id"],
                "user_query": row["user_query"],
                "ai_response": row["ai_response"],
                "user_rating": int(row["user_rating"]),
                "model_id": row["model_id"],
                "created_at": row["created_at"].isoformat() + "Z",
                "retrieval_chunks": row["retrieval_chunks"],
                "test_config": row.get("test_config")
            })

        result = {
            "items": items,
            "total": total,
            "page": request.page,
            "page_size": request.page_size,
            "total_pages": (total + request.page_size - 1) // request.page_size
        }

        logger.info("Demo data search completed",
                   total_results=total,
                   page=request.page,
                   items_returned=len(items))

        return result

    async def get_session_details(self, session_id: str) -> List[SessionDetail]:
        """获取指定会话的详细信息"""
        logger.info("Getting session details", session_id=session_id)

        try:
            # 使用BigQuery服务获取会话详情
            conversations = await self.bigquery_service.get_session_conversations(session_id)

            if not conversations:
                logger.warning("Session not found in BigQuery", session_id=session_id)
                # 回退到演示数据
                return await self._get_session_details_demo(session_id)

            # 转换为SessionDetail对象
            details = []
            for conv in conversations:
                # 获取检索片段
                retrieval_chunks = []
                if conv.retrieval_chunk_ids:
                    chunks = await self.bigquery_service.get_chunks_by_ids(conv.retrieval_chunk_ids)
                    retrieval_chunks = [
                        {
                            "id": chunk.chunk_id,
                            "title": chunk.title,
                            "content": chunk.content
                        }
                        for chunk in chunks
                    ]

                if conv.message_type == "user":
                    detail = SessionDetail(
                        session_id=conv.session_id,
                        model_id=conv.model_id,
                        user_query=conv.content,
                        ai_response="",
                        created_at=conv.timestamp,
                        retrieval_chunks=retrieval_chunks,
                        user_feedback=None
                    )
                    details.append(detail)

            logger.info("Session details retrieved via BigQuery",
                       session_id=session_id,
                       record_count=len(details))

            return details

        except Exception as e:
            logger.warning("BigQuery session details failed, falling back to demo data",
                          error=str(e), session_id=session_id)
            return await self._get_session_details_demo(session_id)

    async def _get_session_details_demo(self, session_id: str) -> List[SessionDetail]:
        """使用演示数据获取会话详情"""
        logger.info("Getting session details from demo data", session_id=session_id)

        # 查找指定会话的所有记录
        session_data = self.df[self.df['session_id'] == session_id].sort_values('created_at')

        if session_data.empty:
            logger.warning("Session not found in demo data", session_id=session_id)
            raise ValueError(f"Session {session_id} not found")

        # 转换为SessionDetail对象
        details = []
        for _, row in session_data.iterrows():
            detail = SessionDetail(
                session_id=row["session_id"],
                model_id=row["model_id"],
                user_query=row["user_query"],
                ai_response=row["ai_response"],
                created_at=row["created_at"],
                retrieval_chunks=row["retrieval_chunks"],
                user_feedback=None  # 演示数据中没有user_feedback
            )
            details.append(detail)

        logger.info("Session details retrieved from demo data",
                   session_id=session_id,
                   record_count=len(details))

        return details

    async def get_model_ids(self) -> List[str]:
        """获取所有可用的模型ID列表"""
        logger.info("Getting available model IDs")

        try:
            # 使用BigQuery服务获取模型ID
            model_ids = await self.bigquery_service.get_available_model_ids()

            logger.info("Model IDs retrieved via BigQuery",
                       model_count=len(model_ids),
                       models=model_ids)

            return model_ids

        except Exception as e:
            logger.warning("BigQuery model IDs failed, falling back to demo data", error=str(e))

            # 回退到演示数据
            model_ids = sorted(self.df['model_id'].unique().tolist())

            logger.info("Model IDs retrieved from demo data",
                       model_count=len(model_ids),
                       models=model_ids)

            return model_ids

    async def test_connection(self) -> bool:
        """测试服务连接状态"""
        try:
            # 测试BigQuery服务连接
            connected = await self.bigquery_service.test_connection()

            if connected:
                logger.info("BigQuery connection test successful")
                return True
            else:
                logger.warning("BigQuery connection failed, but demo data is available")
                # 即使BigQuery连接失败，只要有演示数据就返回True
                return len(self.df) > 0

        except Exception as e:
            logger.error("Connection test failed", error=str(e))
            # 检查是否有演示数据可用
            return len(self.df) > 0