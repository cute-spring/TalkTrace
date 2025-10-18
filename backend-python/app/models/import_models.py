from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class ImportTaskStatus(str, Enum):
    """导入任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ImportRequest(BaseModel):
    """导入请求模型"""
    session_ids: List[str] = Field(..., description="会话ID列表")
    default_owner: Optional[str] = Field(None, description="默认所有者")
    default_priority: Optional[str] = Field(None, description="默认优先级")

class ImportPreview(BaseModel):
    """导入预览模型"""
    total_count: int = Field(..., description="总会话数")
    preview_count: int = Field(..., description="预览数量")
    session_ids: List[str] = Field(..., description="预览的会话ID列表")
    message: str = Field(..., description="预览消息")

class ImportTask(BaseModel):
    """导入任务模型"""
    task_id: str
    session_ids: List[str]
    status: ImportTaskStatus = ImportTaskStatus.PENDING
    total: int = 0
    processed: int = 0
    failed: int = 0
    message: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)

class ImportProgress(BaseModel):
    """导入进度模型"""
    task_id: str
    status: ImportTaskStatus
    total: int
    processed: int
    failed: int
    message: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None