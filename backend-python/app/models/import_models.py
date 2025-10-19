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

class DuplicateSessionInfo(BaseModel):
    """重复会话信息模型"""
    session_id: str = Field(..., description="会话ID")
    existing_test_case_id: str = Field(..., description="已存在的测试用例ID")
    existing_test_case_name: str = Field(..., description="已存在的测试用例名称")
    import_date: str = Field(..., description="原导入时间")
    owner: str = Field(..., description="原测试用例负责人")

class ImportValidationResult(BaseModel):
    """导入验证结果模型"""
    valid_sessions: List[str] = Field(..., description="有效会话ID列表")
    duplicate_sessions: List[DuplicateSessionInfo] = Field(..., description="重复会话信息列表")
    can_import_all: bool = Field(..., description="是否可以导入所有会话")
    total_count: int = Field(..., description="总会话数")
    duplicate_count: int = Field(..., description="重复会话数")
    message: str = Field(..., description="验证结果消息")

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
    duplicate_sessions: Optional[List[DuplicateSessionInfo]] = Field(None, description="重复会话信息")
    validation_result: Optional[ImportValidationResult] = Field(None, description="验证结果")

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