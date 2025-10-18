from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List, Dict, Any
from datetime import datetime

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    """通用API响应模型"""
    success: bool
    data: T
    error: Optional[Dict[str, Any]] = None

class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

class HealthCheck(BaseModel):
    """健康检查响应模型"""
    status: str
    service: str
    timestamp: datetime