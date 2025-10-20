"""API响应模型，用于转换为前端期望的camelCase格式"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from app.models.test_case import (
    TestCase, TestCaseStatus, PriorityLevel, DifficultyLevel, Tag,
    ModelConfig, PromptsConfig, RetrievalConfig, TestConfig,
    TurnRecord, CurrentQuery, ChunkMetadata, RetrievedChunk, TestCaseInput,
    PerformanceMetrics, RetrievalQuality, GenerationInfo, ActualExecution,
    UserFeedback, Execution, QualityScores, Analysis
)

class TagResponse(BaseModel):
    """标签响应模型"""
    name: str
    color: Optional[str] = None

class ModelParamsResponse(BaseModel):
    """模型参数响应模型"""
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None

class ModelConfigResponse(BaseModel):
    """模型配置响应模型"""
    name: str
    version: Optional[str] = None
    params: Optional[Dict[str, Any]] = {}

class PromptsConfigResponse(BaseModel):
    """提示词配置响应模型"""
    system: str
    user_instruction: str = Field(..., alias="userInstruction")

class RetrievalConfigResponse(BaseModel):
    """检索配置响应模型"""
    top_k: Optional[int] = Field(None, alias="topK")
    similarity_threshold: Optional[float] = Field(None, alias="similarityThreshold")
    reranker_enabled: Optional[bool] = Field(None, alias="rerankerEnabled")

class TestConfigResponse(BaseModel):
    """测试配置响应模型"""
    model: ModelConfigResponse
    prompts: PromptsConfigResponse
    retrieval: Optional[RetrievalConfigResponse] = None

class RetrievedChunksResponse(BaseModel):
    """检索片段响应模型"""
    id: str
    title: str
    source: str
    content: str
    metadata: Dict[str, Any]

class ChunkMetadataResponse(BaseModel):
    """检索片段元数据响应模型"""
    publish_date: Optional[str] = Field(None, alias="publishDate")
    effective_date: Optional[str] = Field(None, alias="effectiveDate")
    expiration_date: Optional[str] = Field(None, alias="expirationDate")
    chunk_type: Optional[str] = Field(None, alias="chunkType")
    confidence: float
    retrieval_rank: int = Field(..., alias="retrievalRank")

class RetrievedChunkResponse(BaseModel):
    """检索片段响应模型"""
    id: str
    title: str
    source: str
    content: str
    metadata: ChunkMetadataResponse

class ConversationHistoryResponse(BaseModel):
    """对话历史响应模型"""
    turn: int
    role: str
    query: Optional[str] = None
    response: Optional[str] = None
    retrieved_chunks: Optional[List[Union[str, 'RetrievedChunkResponse']]] = Field(None, alias="retrievedChunks")
    timestamp: str

class CurrentQueryResponse(BaseModel):
    """当前查询响应模型"""
    text: str
    timestamp: str

class TestCaseInputResponse(BaseModel):
    """测试用例输入响应模型"""
    current_query: CurrentQueryResponse = Field(..., alias="currentQuery")
    conversation_history: List[ConversationHistoryResponse] = Field([], alias="conversationHistory")
    current_retrieved_chunks: List[RetrievedChunkResponse] = Field([], alias="currentRetrievedChunks")

class PerformanceMetricsResponse(BaseModel):
    """性能指标响应模型"""
    total_response_time: float = Field(..., alias="totalResponseTime")
    retrieval_time: float = Field(..., alias="retrievalTime")
    generation_time: float = Field(..., alias="generationTime")
    tokens_used: int = Field(..., alias="tokensUsed")
    chunks_considered: int = Field(..., alias="chunksConsidered")

class RetrievalQualityResponse(BaseModel):
    """检索质量响应模型"""
    max_similarity: Optional[float] = Field(None, alias="maxSimilarity")
    avg_similarity: Optional[float] = Field(None, alias="avgSimilarity")
    diversity_score: Optional[float] = Field(None, alias="diversityScore")

class ActualExecutionResponse(BaseModel):
    """实际执行结果响应模型"""
    response: str
    performance_metrics: PerformanceMetricsResponse = Field(..., alias="performanceMetrics")
    retrieval_quality: Optional[RetrievalQualityResponse] = Field(None, alias="retrievalQuality")

class UserFeedbackResponse(BaseModel):
    """用户反馈响应模型"""
    rating: int
    category: str
    comment: str
    concern: str
    suggested_improvement: Optional[str] = Field(None, alias="suggestedImprovement")
    feedback_date: str = Field(..., alias="feedbackDate")
    feedback_source: str = Field(..., alias="feedbackSource")

class ExecutionResponse(BaseModel):
    """执行信息响应模型"""
    actual: ActualExecutionResponse
    user_feedback: Optional[UserFeedbackResponse] = Field(None, alias="userFeedback")

class QualityScoresResponse(BaseModel):
    """质量评分响应模型"""
    context_understanding: int = Field(..., alias="contextUnderstanding")
    answer_accuracy: int = Field(..., alias="answerAccuracy")
    answer_completeness: int = Field(..., alias="answerCompleteness")
    clarity: int
    citation_quality: int = Field(..., alias="citationQuality")

class AnalysisResponse(BaseModel):
    """分析信息响应模型"""
    issue_type: str = Field(..., alias="issueType")
    root_cause: str = Field(..., alias="rootCause")
    expected_answer: str = Field(..., alias="expectedAnswer")
    acceptance_criteria: str = Field(..., alias="acceptanceCriteria")
    quality_scores: QualityScoresResponse = Field(..., alias="qualityScores")
    optimization_suggestions: List[str] = Field([], alias="optimizationSuggestions")
    notes: str
    analyzed_by: str = Field(..., alias="analyzedBy")
    analysis_date: str = Field(..., alias="analysisDate")

class TestCaseMetadataResponse(BaseModel):
    """测试用例元数据响应模型"""
    status: str
    owner: str
    priority: str
    tags: List[TagResponse]
    version: str
    created_date: str = Field(..., alias="createdDate")
    updated_date: Optional[str] = Field(None, alias="updatedDate")
    source_session: str = Field(..., alias="sourceSession")

class TestCaseResponse(BaseModel):
    """测试用例响应模型 - 前端期望的camelCase格式"""
    id: str
    name: str
    description: Optional[str] = None
    status: str
    owner: str
    priority: str
    tags: List[str]
    version: str
    created_date: str = Field(..., alias="createdDate")
    updated_date: Optional[str] = Field(None, alias="updatedDate")
    source_session: str = Field(..., alias="sourceSession")
    domain: str
    difficulty: str
    test_config: TestConfigResponse = Field(..., alias="testConfig")
    input: TestCaseInputResponse = Field(..., alias="input")
    execution: ExecutionResponse = Field(..., alias="execution")
    analysis: Optional[AnalysisResponse] = Field(None, alias="analysis")

    @staticmethod
    def _process_conversation_retrieved_chunks(retrieved_chunks):
        """处理对话历史中的检索片段，支持字符串和对象两种格式"""
        if not retrieved_chunks:
            return []

        processed_chunks = []
        for chunk in retrieved_chunks:
            if isinstance(chunk, str):
                # 如果是字符串，保持原样
                processed_chunks.append(chunk)
            elif hasattr(chunk, 'id') and hasattr(chunk, 'title'):
                # 如果是RetrievedChunk对象，转换为响应格式
                processed_chunks.append(RetrievedChunkResponse(
                    id=chunk.id,
                    title=chunk.title,
                    source=chunk.source,
                    content=chunk.content,
                    metadata=ChunkMetadataResponse(
                        publish_date=getattr(chunk.metadata, 'publish_date', None),
                        effective_date=getattr(chunk.metadata, 'effective_date', None),
                        expiration_date=getattr(chunk.metadata, 'expiration_date', None),
                        chunk_type=getattr(chunk.metadata, 'chunk_type', None),
                        confidence=getattr(chunk.metadata, 'confidence', 0.0),
                        retrieval_rank=getattr(chunk.metadata, 'retrieval_rank', 1)
                    )
                ))
        return processed_chunks

    @classmethod
    def from_test_case(cls, test_case: TestCase) -> "TestCaseResponse":
        """从内部TestCase模型转换为前端响应格式"""
        metadata = test_case.metadata

        # 转换标签：从Tag对象列表转换为字符串列表
        tags = []
        if hasattr(metadata, 'tags') and metadata.tags:
            tags = [tag.name if hasattr(tag, 'name') else tag for tag in metadata.tags]

        return cls(
            id=test_case.id,
            name=test_case.name,
            description=test_case.description,
            status=metadata.status.value if hasattr(metadata.status, 'value') else str(metadata.status),
            owner=metadata.owner,
            priority=metadata.priority.value if hasattr(metadata.priority, 'value') else str(metadata.priority),
            tags=tags,
            version=metadata.version,
            created_date=metadata.created_date,
            updated_date=metadata.updated_date,
            source_session=metadata.source_session,
            domain=test_case.domain,
            difficulty=test_case.difficulty.value if hasattr(test_case.difficulty, 'value') else str(test_case.difficulty),
            test_config=TestConfigResponse(
                model=ModelConfigResponse(
                    name=test_case.test_config.model.name,
                    version=test_case.test_config.model.version,
                    params=test_case.test_config.model.params
                ),
                prompts=PromptsConfigResponse(
                    system=test_case.test_config.prompts.system,
                    user_instruction=test_case.test_config.prompts.user_instruction
                ),
                retrieval=RetrievalConfigResponse(
                    top_k=test_case.test_config.retrieval.top_k if test_case.test_config.retrieval else None,
                    similarity_threshold=test_case.test_config.retrieval.similarity_threshold if test_case.test_config.retrieval else None,
                    reranker_enabled=test_case.test_config.retrieval.reranker_enabled if test_case.test_config.retrieval else None
                ) if test_case.test_config.retrieval else None
            ),
            input=TestCaseInputResponse(
                current_query=CurrentQueryResponse(
                    text=test_case.input.current_query.text,
                    timestamp=test_case.input.current_query.timestamp
                ),
                conversation_history=[
                    ConversationHistoryResponse(
                        turn=turn.turn,
                        role=turn.role,
                        query=turn.query,
                        response=turn.response,
                        retrieved_chunks=self._process_conversation_retrieved_chunks(turn.retrieved_chunks),
                        timestamp=turn.timestamp
                    ) for turn in test_case.input.conversation_history
                ],
                current_retrieved_chunks=[
                    RetrievedChunkResponse(
                        id=chunk.id,
                        title=chunk.title,
                        source=chunk.source,
                        content=chunk.content,
                        metadata=ChunkMetadataResponse(
                            publish_date=chunk.metadata.publish_date,
                            effective_date=chunk.metadata.effective_date,
                            expiration_date=chunk.metadata.expiration_date,
                            chunk_type=chunk.metadata.chunk_type,
                            confidence=chunk.metadata.confidence,
                            retrieval_rank=chunk.metadata.retrieval_rank
                        )
                    ) for chunk in test_case.input.current_retrieved_chunks
                ]
            ),
            execution=ExecutionResponse(
                actual=ActualExecutionResponse(
                    response=test_case.execution.actual.response,
                    performance_metrics=PerformanceMetricsResponse(
                        total_response_time=test_case.execution.actual.performance_metrics.total_response_time,
                        retrieval_time=test_case.execution.actual.performance_metrics.retrieval_time,
                        generation_time=test_case.execution.actual.performance_metrics.generation_time,
                        tokens_used=test_case.execution.actual.performance_metrics.tokens_used,
                        chunks_considered=test_case.execution.actual.performance_metrics.chunks_considered
                    ),
                    retrieval_quality=RetrievalQualityResponse(
                        max_similarity=test_case.execution.actual.retrieval_quality.max_similarity,
                        avg_similarity=test_case.execution.actual.retrieval_quality.avg_similarity,
                        diversity_score=test_case.execution.actual.retrieval_quality.diversity_score
                    ) if test_case.execution.actual.retrieval_quality else None
                ),
                user_feedback=UserFeedbackResponse(
                    rating=test_case.execution.user_feedback.rating,
                    category=test_case.execution.user_feedback.category,
                    comment=test_case.execution.user_feedback.comment,
                    concern=test_case.execution.user_feedback.concern,
                    suggested_improvement=test_case.execution.user_feedback.suggested_improvement,
                    feedback_date=test_case.execution.user_feedback.feedback_date,
                    feedback_source=getattr(test_case.execution.user_feedback, 'feedback_source', 'user')
                ) if test_case.execution.user_feedback else None
            ),
            analysis=AnalysisResponse(
                issue_type=test_case.analysis.issue_type,
                root_cause=test_case.analysis.root_cause,
                expected_answer=test_case.analysis.expected_answer,
                acceptance_criteria=test_case.analysis.acceptance_criteria,
                quality_scores=QualityScoresResponse(
                    context_understanding=test_case.analysis.quality_scores.context_understanding,
                    answer_accuracy=test_case.analysis.quality_scores.answer_accuracy,
                    answer_completeness=test_case.analysis.quality_scores.answer_completeness,
                    clarity=test_case.analysis.quality_scores.clarity,
                    citation_quality=test_case.analysis.quality_scores.citation_quality
                ),
                optimization_suggestions=test_case.analysis.optimization_suggestions,
                notes=test_case.analysis.notes,
                analyzed_by=test_case.analysis.analyzed_by,
                analysis_date=test_case.analysis.analysis_date
            ) if test_case.analysis else None
        )