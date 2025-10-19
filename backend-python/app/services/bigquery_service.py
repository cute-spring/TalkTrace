"""BigQuery服务抽象接口"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
from datetime import datetime
from pydantic import BaseModel

class ConversationRow(BaseModel):
    """对话记录模型（对应BigQuery conversations表）"""
    model_config = {"protected_namespaces": ()}

    # 主要字段
    conversation_id: str
    session_id: str
    message_id: str
    message_type: str  # 'user' | 'assistant' | 'system'
    content: str
    model_id: str
    timestamp: datetime

    # 元数据
    metadata: Dict[str, Any] = {}
    user_rating: Optional[int] = None
    feedback_text: Optional[str] = None
    token_count: Optional[int] = None
    processing_time_ms: Optional[int] = None

    # 检索相关
    retrieval_chunk_ids: List[str] = []

class RetrievalChunkRow(BaseModel):
    """检索片段模型（对应BigQuery retrieval_chunks表）"""
    model_config = {"protected_namespaces": ()}

    # 主要字段
    chunk_id: str
    document_id: str
    chunk_index: int
    content: str
    title: Optional[str] = None

    # 向量化和检索信息
    embedding_vector: Optional[List[float]] = None
    similarity_score: Optional[float] = None

    # 元数据
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

class ConversationQueryRequest(BaseModel):
    """对话查询请求"""
    model_config = {"protected_namespaces": ()}

    # 时间范围
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    # 过滤条件
    model_ids: Optional[List[str]] = None
    session_ids: Optional[List[str]] = None
    message_types: Optional[List[str]] = None

    # 搜索条件
    keywords: Optional[str] = None
    min_rating: Optional[int] = None
    max_rating: Optional[int] = None

    # 分页
    limit: int = 100
    offset: int = 0

    # 排序
    order_by: str = "timestamp"
    order_direction: str = "desc"  # "asc" | "desc"

class RetrievalChunkQueryRequest(BaseModel):
    """检索片段查询请求"""
    model_config = {"protected_namespaces": ()}

    # 文档过滤
    document_ids: Optional[List[str]] = None

    # 内容搜索
    keywords: Optional[str] = None

    # 相似度过滤
    min_similarity: Optional[float] = None
    max_similarity: Optional[float] = None

    # 分页
    limit: int = 100
    offset: int = 0

    # 排序
    order_by: str = "created_at"
    order_direction: str = "desc"

class BigQueryService(ABC):
    """BigQuery服务抽象基类"""

    @abstractmethod
    async def test_connection(self) -> bool:
        """测试连接状态"""
        pass

    @abstractmethod
    async def query_conversations(self, request: ConversationQueryRequest) -> List[ConversationRow]:
        """查询对话记录"""
        pass

    @abstractmethod
    async def count_conversations(self, request: ConversationQueryRequest) -> int:
        """统计对话记录数量"""
        pass

    @abstractmethod
    async def get_conversation_by_id(self, conversation_id: str) -> Optional[ConversationRow]:
        """根据ID获取对话记录"""
        pass

    @abstractmethod
    async def get_session_conversations(self, session_id: str) -> List[ConversationRow]:
        """获取会话的所有对话"""
        pass

    @abstractmethod
    async def query_retrieval_chunks(self, request: RetrievalChunkQueryRequest) -> List[RetrievalChunkRow]:
        """查询检索片段"""
        pass

    @abstractmethod
    async def count_retrieval_chunks(self, request: RetrievalChunkQueryRequest) -> int:
        """统计检索片段数量"""
        pass

    @abstractmethod
    async def get_chunk_by_id(self, chunk_id: str) -> Optional[RetrievalChunkRow]:
        """根据ID获取检索片段"""
        pass

    @abstractmethod
    async def get_chunks_by_ids(self, chunk_ids: List[str]) -> List[RetrievalChunkRow]:
        """根据ID列表批量获取检索片段"""
        pass

    @abstractmethod
    async def get_available_model_ids(self) -> List[str]:
        """获取所有可用的模型ID"""
        pass

    @abstractmethod
    async def get_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """获取会话统计信息"""
        pass

    @abstractmethod
    async def stream_conversations(self, request: ConversationQueryRequest) -> AsyncIterator[ConversationRow]:
        """流式查询对话记录（用于大数据量查询）"""
        pass