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
    session_ids: List[str] = Field(..., description="会话ID列表", alias="session_ids")
    default_owner: Optional[str] = Field(None, description="默认所有者", alias="defaultOwner")
    default_priority: Optional[str] = Field(None, description="默认优先级", alias="defaultPriority")
    default_difficulty: Optional[str] = Field(None, description="默认难度", alias="defaultDifficulty")
    include_analysis: Optional[bool] = Field(False, description="是否包含分析数据", alias="includeAnalysis")

    model_config = {"populate_by_name": True}

class ImportPreview(BaseModel):
    """导入预览模型"""
    total_count: int = Field(..., description="总会话数")
    preview_count: int = Field(..., description="预览数量")
    session_ids: List[str] = Field(..., description="预览的会话ID列表")
    message: str = Field(..., description="预览消息")
    preview_data: Optional[List[dict]] = Field(None, description="预览的会话数据")

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
    config: Optional[dict] = Field(None, description="导入配置参数")

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