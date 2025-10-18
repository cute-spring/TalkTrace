from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TestCaseStatus(str, Enum):
    """测试用例状态枚举"""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class PriorityLevel(str, Enum):
    """优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class DifficultyLevel(str, Enum):
    """难度等级枚举"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class Tag(BaseModel):
    """标签模型"""
    name: str
    color: Optional[str] = None

class TestCase(BaseModel):
    """测试用例模型"""
    id: str
    name: str
    description: Optional[str] = None
    status: TestCaseStatus = TestCaseStatus.DRAFT
    owner: str
    priority: PriorityLevel = PriorityLevel.MEDIUM
    domain: str
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    created_date: datetime
    updated_date: Optional[datetime] = None
    tags: List[Tag] = []

class TestCaseCreate(BaseModel):
    """创建测试用例请求模型"""
    name: str
    description: Optional[str] = None
    owner: str
    priority: PriorityLevel = PriorityLevel.MEDIUM
    domain: str
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    tags: List[Tag] = []

class TestCaseUpdate(BaseModel):
    """更新测试用例请求模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TestCaseStatus] = None
    priority: Optional[PriorityLevel] = None
    difficulty: Optional[DifficultyLevel] = None
    tags: Optional[List[Tag]] = None

class BatchOperation(BaseModel):
    """批量操作请求模型"""
    action: str = Field(..., description="操作类型")
    ids: List[str] = Field(..., description="测试用例ID列表")
    data: Optional[Dict[str, Any]] = None