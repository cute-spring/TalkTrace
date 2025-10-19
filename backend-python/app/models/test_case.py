from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TestCaseStatus(str, Enum):
    """测试用例状态枚举"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    PUBLISHED = "published"
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

# Comprehensive test case data models
class ModelConfig(BaseModel):
    """模型配置"""
    name: str
    version: Optional[str] = None
    params: Dict[str, Any] = {}

class PromptsConfig(BaseModel):
    """提示词配置"""
    system: str
    user_instruction: str

class RetrievalConfig(BaseModel):
    """检索配置"""
    top_k: Optional[int] = None
    similarity_threshold: Optional[float] = None
    reranker_enabled: Optional[bool] = None

class TestConfig(BaseModel):
    """测试配置"""
    model: ModelConfig
    prompts: PromptsConfig
    retrieval: Optional[RetrievalConfig] = None

class TurnRecord(BaseModel):
    """对话轮次记录"""
    turn: int
    role: str  # "user" | "assistant" | "system"
    query: Optional[str] = None
    response: Optional[str] = None
    retrieved_chunks: Optional[List[str]] = None
    timestamp: str

class CurrentQuery(BaseModel):
    """当前查询"""
    text: str
    timestamp: str

class ChunkMetadata(BaseModel):
    """检索片段元数据"""
    publish_date: Optional[str] = None
    effective_date: Optional[str] = None
    expiration_date: Optional[str] = None
    chunk_type: Optional[str] = None
    confidence: float
    retrieval_rank: int

class RetrievedChunk(BaseModel):
    """检索片段"""
    id: str
    title: str
    source: str
    content: str
    metadata: ChunkMetadata

class TestCaseInput(BaseModel):
    """测试用例输入"""
    current_query: CurrentQuery
    conversation_history: List[TurnRecord] = []
    current_retrieved_chunks: List[RetrievedChunk] = []

class PerformanceMetrics(BaseModel):
    """性能指标"""
    total_response_time: float
    retrieval_time: float
    generation_time: float
    tokens_used: int
    chunks_considered: int

class RetrievalQuality(BaseModel):
    """检索质量"""
    max_similarity: Optional[float] = None
    avg_similarity: Optional[float] = None
    diversity_score: Optional[float] = None

class GenerationInfo(BaseModel):
    """生成信息"""
    reasoning_chain: Optional[str] = None
    citation_usage: Optional[List[str]] = None

class ActualExecution(BaseModel):
    """实际执行结果"""
    response: str
    performance_metrics: PerformanceMetrics
    retrieval_quality: Optional[RetrievalQuality] = None
    generation_info: Optional[GenerationInfo] = None

class UserFeedback(BaseModel):
    """用户反馈"""
    rating: int
    category: str
    comment: str
    concern: str
    suggested_improvement: Optional[str] = None
    feedback_date: str
    feedback_source: str

class Execution(BaseModel):
    """执行信息"""
    actual: ActualExecution
    user_feedback: Optional[UserFeedback] = None

class QualityScores(BaseModel):
    """质量评分"""
    context_understanding: int
    answer_accuracy: int
    answer_completeness: int
    clarity: int
    citation_quality: int

class Analysis(BaseModel):
    """分析信息"""
    issue_type: str
    root_cause: str
    expected_answer: str
    acceptance_criteria: str
    quality_scores: QualityScores
    optimization_suggestions: List[str] = []
    notes: str
    analyzed_by: str
    analysis_date: str

class TestCaseMetadata(BaseModel):
    """测试用例元数据"""
    status: TestCaseStatus
    owner: str
    priority: PriorityLevel
    tags: List[Tag] = []
    version: str
    created_date: str
    updated_date: Optional[str] = None
    source_session: str

class TestCase(BaseModel):
    """完整测试用例模型"""
    id: str
    name: str
    description: Optional[str] = None
    metadata: TestCaseMetadata
    domain: str
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    test_config: TestConfig
    input: TestCaseInput
    execution: Execution
    analysis: Optional[Analysis] = None

class TestCaseCreate(BaseModel):
    """创建测试用例请求模型"""
    name: str
    description: Optional[str] = None
    owner: str
    priority: PriorityLevel = PriorityLevel.MEDIUM
    domain: str
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    tags: List[Tag] = []
    test_config: TestConfig
    input: TestCaseInput
    execution: Execution
    analysis: Optional[Analysis] = None
    metadata: Optional[TestCaseMetadata] = None

class TestCaseUpdate(BaseModel):
    """更新测试用例请求模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[TestCaseMetadata] = None
    domain: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    test_config: Optional[TestConfig] = None
    input: Optional[TestCaseInput] = None
    execution: Optional[Execution] = None
    analysis: Optional[Analysis] = None

class BatchOperation(BaseModel):
    """批量操作请求模型"""
    action: str = Field(..., description="操作类型")
    ids: List[str] = Field(..., description="测试用例ID列表")
    data: Optional[Dict[str, Any]] = None