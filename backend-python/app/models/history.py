from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class RetrievalChunk(BaseModel):
    """检索片段模型"""
    model_config = {"protected_namespaces": ()}
    id: str
    title: str
    content: str

class HistoryRecord(BaseModel):
    """历史记录模型"""
    model_config = {"protected_namespaces": ()}
    session_id: str
    user_query: str
    ai_response: str
    user_rating: int = Field(ge=1, le=5, description="用户评分，1-5星")
    model_id: str
    created_at: datetime
    retrieval_chunks: List[RetrievalChunk] = []

class HistorySearchRequest(BaseModel):
    """历史记录搜索请求模型"""
    model_config = {"protected_namespaces": ()}
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    model_ids: Optional[List[str]] = Field(None, description="模型ID列表")
    rating_range: Optional[tuple[int, int]] = Field(None, description="评分范围，例如(1,3)")
    keywords: Optional[str] = Field(None, description="关键词搜索")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页大小")

class SessionDetail(BaseModel):
    """会话详情模型"""
    model_config = {"protected_namespaces": ()}
    session_id: str
    model_id: str
    user_query: str
    ai_response: str
    created_at: datetime
    retrieval_chunks: List[RetrievalChunk]
    user_feedback: Optional[str] = None
    test_config: Optional[Dict[str, Any]] = None