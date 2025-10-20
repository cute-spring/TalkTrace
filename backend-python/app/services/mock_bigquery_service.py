"""Mock BigQuery服务实现"""
import asyncio
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, AsyncIterator
import pandas as pd

from app.services.bigquery_service import (
    BigQueryService,
    ConversationRow,
    RetrievalChunkRow,
    ConversationQueryRequest,
    RetrievalChunkQueryRequest
)
from app.utils.logger import logger

class MockBigQueryService(BigQueryService):
    """Mock BigQuery服务实现"""

    def __init__(self):
        """初始化Mock BigQuery服务"""
        logger.info("Initializing MockBigQueryService")
        self._conversations_data: List[ConversationRow] = []
        self._retrieval_chunks_data: List[RetrievalChunkRow] = []
        self._initialize_data()

    def _initialize_data(self):
        """初始化模拟数据"""
        logger.info("Generating mock BigQuery data")

        # 生成检索片段数据
        self._generate_retrieval_chunks()

        # 生成对话数据
        self._generate_conversations()

        logger.info(
            "Mock data initialized",
            conversations_count=len(self._conversations_data),
            chunks_count=len(self._retrieval_chunks_data)
        )

    def _generate_retrieval_chunks(self):
        """生成检索片段数据"""
        # 预定义的文档和主题
        documents = [
            {"id": "doc_finance_001", "title": "投资基金基础知识", "topic": "finance"},
            {"id": "doc_finance_002", "title": "股票投资指南", "topic": "finance"},
            {"id": "doc_tech_001", "title": "人工智能基础概念", "topic": "technology"},
            {"id": "doc_tech_002", "title": "React Router配置", "topic": "technology"},
            {"id": "doc_tech_003", "title": "Python装饰器详解", "topic": "programming"},
            {"id": "doc_tech_004", "title": "微服务架构原理", "topic": "architecture"},
            {"id": "doc_security_001", "title": "网络安全最佳实践", "topic": "security"},
            {"id": "doc_dev_001", "title": "数据库优化技巧", "topic": "development"},
            {"id": "doc_dev_002", "title": "API设计原则", "topic": "development"},
            {"id": "doc_ops_001", "title": "DevOps实践指南", "topic": "operations"}
        ]

        # 为每个文档生成多个片段
        chunk_contents = {
            "finance": [
                "投资基金是一种集合投资工具，通过专业基金经理管理资金，投资于多种证券组合。",
                "基金投资的主要优势包括分散风险、专业管理、流动性好、门槛低等。",
                "股票投资代表对公司的所有权，投资者通过购买股票成为公司股东。",
                "股票投资风险较高，但潜在回报也较大，需要投资者具备相应的风险承受能力。"
            ],
            "technology": [
                "人工智能是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
                "机器学习是人工智能的子集，通过算法使计算机能够从数据中学习并做出预测。",
                "React Router是React应用中用于管理路由的库，支持声明式路由配置。",
                "装饰器是Python中一种修改函数或类的机制，允许在不改变原始代码的情况下添加功能。"
            ],
            "programming": [
                "Python装饰器本质上是一个函数，它接受另一个函数作为参数并返回一个新的函数。",
                "装饰器常用于日志记录、性能监控、权限验证等横切关注点的处理。",
                "闭包是指函数能够访问其外部作用域中的变量，即使在外部函数执行完毕后。"
            ],
            "architecture": [
                "微服务架构是一种将应用程序拆分为小型、独立服务的架构风格。",
                "每个微服务都运行在自己的进程中，通过轻量级机制进行通信。",
                "微服务架构的优势包括独立部署、技术多样性、弹性伸缩等。"
            ],
            "security": [
                "网络安全最佳实践包括使用强密码、启用多因素认证、定期更新软件等。",
                "SQL注入攻击是常见的Web应用安全威胁，应使用参数化查询来防范。",
                "XSS攻击可以通过输入验证、输出编码和使用内容安全策略来防范。"
            ],
            "development": [
                "数据库优化技巧包括创建适当的索引、避免N+1查询、使用连接池等。",
                "API设计应遵循RESTful原则，使用合适的HTTP方法和状态码。",
                "代码重构是改善代码结构而不改变其外部行为的过程。"
            ],
            "operations": [
                "DevOps实践强调开发和运维团队的协作，通过自动化工具提高效率。",
                "持续集成/持续部署(CI/CD)是DevOps的核心实践，自动化代码构建、测试和部署过程。",
                "基础设施即代码(IaC)使用代码来管理和配置基础设施，提高一致性和可重复性。"
            ]
        }

        base_time = datetime.now() - timedelta(days=30)

        for doc in documents:
            topic = doc["topic"]
            contents = chunk_contents.get(topic, ["默认内容"])

            for i, content in enumerate(contents):
                # 生成完整的元数据
                publish_date = (base_time + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
                effective_date = (base_time + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
                expiration_date = (base_time + timedelta(days=365, hours=random.randint(0, 720))).strftime("%Y-%m-%d")

                # 根据主题确定chunk类型
                chunk_type_map = {
                    "finance": "conceptual",
                    "technology": "tutorial",
                    "programming": "code",
                    "architecture": "architectural",
                    "security": "guideline",
                    "development": "best_practice",
                    "operations": "procedural"
                }
                chunk_type = chunk_type_map.get(topic, "text")

                # 生成来源URL
                source_urls = {
                    "finance": "https://internal.com/finance/",
                    "technology": "https://internal.com/tech/",
                    "programming": "https://internal.com/dev/",
                    "architecture": "https://internal.com/arch/",
                    "security": "https://internal.com/security/",
                    "development": "https://internal.com/dev/",
                    "operations": "https://internal.com/ops/"
                }
                source_url = f"{source_urls.get(topic, 'https://internal.com/docs/')}{doc['id'].replace('_', '-')}"

                chunk = RetrievalChunkRow(
                    chunk_id=f"CH-{(1000 + len(self._retrieval_chunks_data) + 1):04d}",
                    document_id=doc["id"],
                    chunk_index=i,
                    content=content,
                    title=f"{doc['title']} - 片段{i+1}",
                    embedding_vector=[random.random() for _ in range(768)],  # 模拟向量
                    similarity_score=random.uniform(0.5, 1.0),
                    metadata={
                        "topic": topic,
                        "document_title": doc["title"],
                        "word_count": len(content),
                        "language": "zh-CN",
                        # 完整的检索片段元数据字段
                        "publish_date": publish_date,
                        "effective_date": effective_date,
                        "expiration_date": expiration_date,
                        "chunk_type": chunk_type,
                        "source": source_url,
                        "author": "expert@company.com",
                        "reviewer": "reviewer@company.com",
                        "confidence": random.uniform(0.75, 0.95),
                        "retrieval_rank": i + 1,
                        "tags": [topic, doc["id"].split("_")[0]],
                        "category": topic,
                        "subcategory": doc["id"].split("_")[1] if "_" in doc["id"] else "general"
                    },
                    created_at=base_time + timedelta(hours=random.randint(0, 720)),
                    updated_at=base_time + timedelta(hours=random.randint(0, 720))
                )
                self._retrieval_chunks_data.append(chunk)

    def _generate_conversations(self):
        """生成对话数据"""
        models = ["gpt-4o-mini", "gpt-4o", "claude-3-sonnet", "claude-3-haiku"]

        # 预定义的对话主题和内容
        conversation_templates = [
            {
                "topic": "投资基金",
                "user_queries": [
                    "请帮我比较一下投资基金和股票投资的优缺点",
                    "投资基金有哪些类型？我该如何选择？",
                    "投资基金的风险如何控制？"
                ],
                "ai_responses": [
                    "投资基金和股票投资各有优势。基金投资具有分散风险、专业管理等特点...",
                    "投资基金主要分为股票型、债券型、混合型、货币型等。选择时需考虑您的风险承受能力...",
                    "投资基金的风险可以通过资产配置、定期定额投资、长期持有等方式来控制..."
                ]
            },
            {
                "topic": "人工智能",
                "user_queries": [
                    "什么是人工智能？它有哪些应用领域？",
                    "机器学习和深度学习有什么区别？",
                    "AI技术对未来社会会有什么影响？"
                ],
                "ai_responses": [
                    "人工智能是模拟人类智能的计算机系统，应用领域包括自然语言处理、计算机视觉等...",
                    "机器学习是AI的子集，而深度学习是机器学习的一个分支，使用神经网络进行学习...",
                    "AI技术将深刻改变社会，提高生产效率，但也需要关注就业影响和伦理问题..."
                ]
            },
            {
                "topic": "React开发",
                "user_queries": [
                    "如何配置React项目的路由？",
                    "React Hooks的使用方法是什么？",
                    "React性能优化有哪些技巧？"
                ],
                "ai_responses": [
                    "可以使用React Router库来配置路由，首先安装react-router-dom包...",
                    "React Hooks允许在函数组件中使用状态和其他React特性，如useState、useEffect等...",
                    "React性能优化技巧包括使用React.memo、useMemo、useCallback，以及虚拟化长列表等..."
                ]
            }
        ]

        base_time = datetime.now() - timedelta(days=7)

        # 生成session_mock_xxxx会话 (20个)
        for session_idx in range(1, 21):
            session_id = f"session_mock_{session_idx:04d}"
            template = random.choice(conversation_templates)
            model = random.choice(models)

            # 每个会话生成1-3轮对话
            num_turns = random.randint(1, 3)
            session_time = base_time + timedelta(hours=session_idx * 2)

            for turn in range(num_turns):
                query_idx = min(turn, len(template["user_queries"]) - 1)
                user_query = template["user_queries"][query_idx]
                ai_response = template["ai_responses"][query_idx]

                # 生成用户消息
                user_message = ConversationRow(
                    conversation_id=f"conv_{session_id}_user_{turn+1}",
                    session_id=session_id,
                    message_id=f"msg_{session_id}_user_{turn+1}",
                    message_type="user",
                    content=user_query,
                    model_id=model,
                    timestamp=session_time + timedelta(minutes=turn * 10),
                    metadata={
                        "topic": template["topic"],
                        "message_length": len(user_query),
                        "language": "zh-CN"
                    },
                    user_rating=None,  # 用户消息没有评分
                    token_count=len(user_query.split()),
                    processing_time_ms=random.randint(100, 500),
                    retrieval_chunk_ids=[]  # 用户消息通常没有检索片段
                )

                # 生成AI回复
                available_chunks = [c.chunk_id for c in self._retrieval_chunks_data if c.metadata.get("topic") == template["topic"]]
                num_chunks = min(random.randint(1, 3), len(available_chunks), 3)  # 确保不超过可用数量
                ai_chunks = random.sample(available_chunks, num_chunks) if available_chunks else []

                ai_message = ConversationRow(
                    conversation_id=f"conv_{session_id}_ai_{turn+1}",
                    session_id=session_id,
                    message_id=f"msg_{session_id}_ai_{turn+1}",
                    message_type="assistant",
                    content=ai_response,
                    model_id=model,
                    timestamp=session_time + timedelta(minutes=turn * 10 + 2),
                    metadata={
                        "topic": template["topic"],
                        "message_length": len(ai_response),
                        "language": "zh-CN",
                        "response_type": "assistant"
                    },
                    user_rating=random.randint(1, 5),
                    token_count=len(ai_response.split()),
                    processing_time_ms=random.randint(500, 2000),
                    retrieval_chunk_ids=ai_chunks
                )

                self._conversations_data.extend([user_message, ai_message])

        # 生成session_gen_xxxx会话，与demo_data.py中的格式匹配 (30个)
        topics = [
            "机器学习算法原理", "数据库优化技巧", "前端性能优化", "云计算服务比较",
            "网络安全最佳实践", "移动开发框架选择", "API设计原则", "代码重构方法",
            "项目管理工具", "DevOps实践指南", "投资基金基础知识", "人工智能应用领域",
            "React开发技巧", "Python编程进阶", "微服务架构设计"
        ]

        for session_idx in range(1, 31):
            session_id = f"session_gen_{session_idx:04d}"
            topic = random.choice(topics)
            model = random.choice(models)

            # 为session_gen会话生成特定的对话内容
            user_query = f"请详细解释{topic}"
            ai_response = f"关于{topic}，这是一个很好的问题。让我为您详细解释。{topic}涉及到多个重要概念和实践要点..."

            # 每个会话生成1-2轮对话
            num_turns = random.randint(1, 2)
            session_time = base_time + timedelta(hours=session_idx * 3 + 100)  # 避免与mock会话时间重叠

            for turn in range(num_turns):
                # 生成用户消息
                user_message = ConversationRow(
                    conversation_id=f"conv_{session_id}_user_{turn+1}",
                    session_id=session_id,
                    message_id=f"msg_{session_id}_user_{turn+1}",
                    message_type="user",
                    content=user_query,
                    model_id=model,
                    timestamp=session_time + timedelta(minutes=turn * 15),
                    metadata={
                        "topic": topic,
                        "message_length": len(user_query),
                        "language": "zh-CN",
                        "data_source": "demo_compatible"
                    },
                    user_rating=None,
                    token_count=len(user_query.split()),
                    processing_time_ms=random.randint(100, 500),
                    retrieval_chunk_ids=[]
                )

                # 生成AI回复
                available_chunks = [c.chunk_id for c in self._retrieval_chunks_data if c.metadata.get("topic") in ["technology", "programming", "development"]]
                num_chunks = min(random.randint(1, 2), len(available_chunks))
                ai_chunks = random.sample(available_chunks, num_chunks) if available_chunks else []

                ai_message = ConversationRow(
                    conversation_id=f"conv_{session_id}_ai_{turn+1}",
                    session_id=session_id,
                    message_id=f"msg_{session_id}_ai_{turn+1}",
                    message_type="assistant",
                    content=ai_response,
                    model_id=model,
                    timestamp=session_time + timedelta(minutes=turn * 15 + 3),
                    metadata={
                        "topic": topic,
                        "message_length": len(ai_response),
                        "language": "zh-CN",
                        "response_type": "assistant",
                        "data_source": "demo_compatible"
                    },
                    user_rating=random.randint(1, 5),
                    token_count=len(ai_response.split()),
                    processing_time_ms=random.randint(500, 2000),
                    retrieval_chunk_ids=ai_chunks
                )

                self._conversations_data.extend([user_message, ai_message])

    async def test_connection(self) -> bool:
        """测试连接状态"""
        try:
            # 模拟连接测试
            await asyncio.sleep(0.1)
            return True
        except Exception as e:
            logger.error("Mock BigQuery connection test failed", error=str(e))
            return False

    async def query_conversations(self, request: ConversationQueryRequest) -> List[ConversationRow]:
        """查询对话记录"""
        logger.info("Querying conversations", request=request.dict())

        # 转换为DataFrame便于过滤
        df = pd.DataFrame([conv.dict() for conv in self._conversations_data])

        if df.empty:
            return []

        # 处理NaN值
        df['user_rating'] = df['user_rating'].fillna(0)
        df['token_count'] = df['token_count'].fillna(0)
        df['processing_time_ms'] = df['processing_time_ms'].fillna(0)

        # 时间过滤
        if request.start_time:
            df = df[df['timestamp'] >= pd.to_datetime(request.start_time)]
        if request.end_time:
            df = df[df['timestamp'] <= pd.to_datetime(request.end_time)]

        # 模型过滤
        if request.model_ids:
            df = df[df['model_id'].isin(request.model_ids)]

        # 会话过滤
        if request.session_ids:
            df = df[df['session_id'].isin(request.session_ids)]

        # 消息类型过滤
        if request.message_types:
            df = df[df['message_type'].isin(request.message_types)]

        # 关键词搜索
        if request.keywords and request.keywords.strip():
            keywords = request.keywords.lower()
            mask = df['content'].str.lower().str.contains(keywords, na=False)
            df = df[mask]

        # 评分过滤（只对assistant消息有效）
        if request.min_rating is not None:
            df = df[(df['user_rating'] >= request.min_rating) | (df['user_rating'].isna())]
        if request.max_rating is not None:
            df = df[(df['user_rating'] <= request.max_rating) | (df['user_rating'].isna())]

        # 排序
        if request.order_by in df.columns:
            ascending = request.order_direction == "asc"
            df = df.sort_values(by=request.order_by, ascending=ascending)

        # 分页
        df = df.iloc[request.offset:request.offset + request.limit]

        # 转换回ConversationRow对象
        results = []
        for _, row in df.iterrows():
            # 将NaN的user_rating转换为None
            if pd.isna(row.get('user_rating')) or row.get('user_rating') == 0:
                row = row.copy()
                row['user_rating'] = None

            results.append(ConversationRow(**row.to_dict()))

        logger.info("Conversation query completed", results_count=len(results))
        return results

    async def count_conversations(self, request: ConversationQueryRequest) -> int:
        """统计对话记录数量"""
        # 重用查询逻辑，但不应用分页
        count_request = request.copy()
        count_request.offset = 0
        count_request.limit = 1000000  # 设置一个很大的限制

        results = await self.query_conversations(count_request)
        return len(results)

    async def get_conversation_by_id(self, conversation_id: str) -> Optional[ConversationRow]:
        """根据ID获取对话记录"""
        for conv in self._conversations_data:
            if conv.conversation_id == conversation_id:
                return conv
        return None

    async def get_session_conversations(self, session_id: str) -> List[ConversationRow]:
        """获取会话的所有对话"""
        return [
            conv for conv in self._conversations_data
            if conv.session_id == session_id
        ]

    async def query_retrieval_chunks(self, request: RetrievalChunkQueryRequest) -> List[RetrievalChunkRow]:
        """查询检索片段"""
        logger.info("Querying retrieval chunks", request=request.dict())

        df = pd.DataFrame([chunk.dict() for chunk in self._retrieval_chunks_data])

        if df.empty:
            return []

        # 处理NaN值
        df['similarity_score'] = df['similarity_score'].fillna(0.0)

        # 文档过滤
        if request.document_ids:
            df = df[df['document_id'].isin(request.document_ids)]

        # 关键词搜索
        if request.keywords and request.keywords.strip():
            keywords = request.keywords.lower()
            mask = (
                df['content'].str.lower().str.contains(keywords, na=False) |
                df['title'].str.lower().str.contains(keywords, na=False)
            )
            df = df[mask]

        # 相似度过滤
        if request.min_similarity is not None:
            df = df[df['similarity_score'] >= request.min_similarity]
        if request.max_similarity is not None:
            df = df[df['similarity_score'] <= request.max_similarity]

        # 排序
        if request.order_by in df.columns:
            ascending = request.order_direction == "asc"
            df = df.sort_values(by=request.order_by, ascending=ascending)

        # 分页
        df = df.iloc[request.offset:request.offset + request.limit]

        # 转换回RetrievalChunkRow对象
        results = []
        for _, row in df.iterrows():
            # 处理None值
            if pd.isna(row.get('similarity_score')):
                row = row.copy()
                row['similarity_score'] = None

            results.append(RetrievalChunkRow(**row.to_dict()))

        logger.info("Retrieval chunks query completed", results_count=len(results))
        return results

    async def count_retrieval_chunks(self, request: RetrievalChunkQueryRequest) -> int:
        """统计检索片段数量"""
        count_request = request.copy()
        count_request.offset = 0
        count_request.limit = 1000000

        results = await self.query_retrieval_chunks(count_request)
        return len(results)

    async def get_chunk_by_id(self, chunk_id: str) -> Optional[RetrievalChunkRow]:
        """根据ID获取检索片段"""
        for chunk in self._retrieval_chunks_data:
            if chunk.chunk_id == chunk_id:
                return chunk
        return None

    async def get_chunks_by_ids(self, chunk_ids: List[str]) -> List[RetrievalChunkRow]:
        """根据ID列表批量获取检索片段"""
        return [
            chunk for chunk in self._retrieval_chunks_data
            if chunk.chunk_id in chunk_ids
        ]

    async def get_available_model_ids(self) -> List[str]:
        """获取所有可用的模型ID"""
        model_ids = list(set(conv.model_id for conv in self._conversations_data))
        return sorted(model_ids)

    async def get_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """获取会话统计信息"""
        session_convs = await self.get_session_conversations(session_id)

        if not session_convs:
            return {}

        user_messages = [conv for conv in session_convs if conv.message_type == "user"]
        ai_messages = [conv for conv in session_convs if conv.message_type == "assistant"]

        ratings = [conv.user_rating for conv in ai_messages if conv.user_rating is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else None

        return {
            "session_id": session_id,
            "total_messages": len(session_convs),
            "user_messages": len(user_messages),
            "ai_messages": len(ai_messages),
            "average_rating": avg_rating,
            "models_used": list(set(conv.model_id for conv in session_convs)),
            "total_tokens": sum(conv.token_count or 0 for conv in session_convs),
            "total_processing_time_ms": sum(conv.processing_time_ms or 0 for conv in session_convs),
            "first_message_time": min(conv.timestamp for conv in session_convs),
            "last_message_time": max(conv.timestamp for conv in session_convs)
        }

    async def stream_conversations(self, request: ConversationQueryRequest) -> AsyncIterator[ConversationRow]:
        """流式查询对话记录"""
        # 简单实现：批量返回结果
        batch_size = 50
        offset = 0

        while True:
            batch_request = request.copy()
            batch_request.offset = offset
            batch_request.limit = batch_size

            batch = await self.query_conversations(batch_request)

            if not batch:
                break

            for conv in batch:
                yield conv

            offset += batch_size

            # 模拟网络延迟
            await asyncio.sleep(0.01)