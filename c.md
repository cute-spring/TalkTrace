请参考下面的数据，重新审视下面的设计的完整性。rephase the design of the following data to review the completeness of the design。 Please don't develope the design before confirming with me.

基于您提供的样本表结构，我来帮您梳理和重新组织这个需求。

## 需求梳理与重新表述

### 项目背景
我们已有一个基于LLM的RAG聊天机器人，所有用户对话历史存储在Google BigQuery的原始对话记录表中。为了系统化地优化AI回答质量，需要构建一个测试样本管理平台，从海量对话中筛选代表性数据，并按照标准化的测试用例格式进行加工和标注。

### 数据表结构

**原始对话记录表 (数据源)**
- 会话ID
- 用户问题、AI回答、对话时间
- model_id, system_prompt_id, user_instruction_id
- chunks (检索到的文档块)

**测试样本表 (目标表)**
包含完整的测试用例结构，如您提供的模板，重点包括：
- 测试用例元数据 (ID, 名称, 状态, 负责人, 优先级等)
- 领域和难度分类
- 模型配置和提示词
- 输入查询和检索到的文档块
- 当前AI回答和用户反馈
- 期望答案和验收标准

### 功能需求

#### 界面一：历史记录查询与导入界面

**核心功能**：从原始对话中快速定位和筛选候选数据，批量导入到测试样本库

#### 界面二：测试样本管理与标注界面

**核心功能**：对导入的测试用例进行精细化管理和质量提升

期望的数据结构和字段设计，可以参考下面的JSON示例：

```json
{
  "success": true,
  "data": {
    "testCase": {
      "id": "TC-0001",
      "name": "测试用例1",
      "status": "draft",
      "owner": "user@example.com",
      "priority": "medium",
      "tags": ["finance", "multi-turn"],
      "version": "1.0",
      "createdDate": "2024-01-15",
      "updatedDate": "2024-01-16",
      "sourceSession": "session_123",
      "domain": "finance",
      "difficulty": "medium",
      "testConfig": {
        "model": {
          "name": "gpt-4o-mini",
          "params": {
            "temperature": 0.0,
            "max_tokens": 512
          }
        },
        "prompts": {
          "system": "You are a helpful assistant...",
          "user_instruction": "Using the provided documents..."
        }
      },
      "input": {
        "currentQuery": "能再解释一下第一个方案的具体风险吗？",
        "conversationHistory": [
          {
            "turn": 1,
            "role": "user",
            "query": "帮我比较一下投资基金和股票投资的优缺点",
            "timestamp": "2024-01-15T10:00:00Z"
          },
          {
            "turn": 2,
            "role": "assistant",
            "response": "投资基金的优势包括...",
            "retrievedChunks": ["CH-1001", "CH-1002"],
            "timestamp": "2024-01-15T10:00:01Z"
          }
        ],
        "currentRetrievedChunks": [
          {
            "id": "CH-1005",
            "title": "投资基金风险管理指南",
            "source": "https://internal.com/finance/fund-risk",
            "content": "投资基金的具体风险包括：...",
            "metadata": {
              "publishDate": "2023-06-01",
              "effectiveDate": "2023-06-01",
              "expirationDate": "2024-12-31",
              "chunkType": "conceptual",
              "confidence": 0.92,
              "retrievalRank": 1
            }
          }
        ]
      },
      "execution": {
        "actual": {
          "response": "投资基金的具体风险包括市场风险...",
          "performanceMetrics": {
            "totalResponseTime": 2.1,
            "retrievalTime": 0.3,
            "generationTime": 1.8,
            "tokensUsed": 345,
            "chunksConsidered": 5
          },
          "retrievalQuality": {
            "maxSimilarity": 0.92,
            "avgSimilarity": 0.78,
            "diversityScore": 0.65
          }
        },
        "userFeedback": {
          "rating": 3,
          "category": "accuracy",
          "comment": "回答列出了风险类型，但没有具体说明如何识别和应对这些风险",
          "concern": "感觉回答比较模板化，缺乏针对性的建议",
          "suggestedImprovement": "希望能举例说明每种风险在什么情况下会发生",
          "feedbackDate": "2024-01-15T10:02:00Z",
          "feedbackSource": "user"
        }
      },
      "analysis": {
        "issueType": "context_understanding",
        "rootCause": "未能正确解析'第一个方案'在对话历史中的指代",
        "expectedAnswer": "您询问的'第一个方案'（投资基金）的具体风险包括：...",
        "acceptanceCriteria": "1. 必须正确识别'第一个方案'指代投资基金...",
        "qualityScores": {
          "contextUnderstanding": 2,
          "answerAccuracy": 4,
          "answerCompleteness": 3,
          "clarity": 3,
          "citationQuality": 4
        },
        "optimizationSuggestions": [
          "改进对话状态跟踪，准确识别历史指代",
          "在回答中增加具体示例提高实用性"
        ],
        "notes": "用户明显在延续之前的对话，但AI未能充分理解上下文。",
        "analyzedBy": "expert@company.com",
        "analysisDate": "2024-01-16"
      }
    }
  }
}


interface TestCaseDetailResponse {
  test_case: {
    id: string;
    name: string;
    description?: string;
    metadata: {
      status: string;
      owner: string;
      priority: string;
      tags: string[];
      version: string;
      created_date: string;
      updated_date: string;
      source_session: string;
    };
    domain: string;
    difficulty: string;
    
    test_config: {
      model: {
        name: string;
        version?: string;
        params: {
          temperature: number;
          max_tokens: number;
          top_p?: number;
        };
      };
      prompts: {
        system: string;
        user_instruction: string;
      };
      retrieval?: {
        top_k: number;
        similarity_threshold: number;
        reranker_enabled: boolean;
      };
    };
    
    input: {
      current_query: {
        text: string;
        timestamp: string;
      };
      conversation_history: Array<{
        turn: number;
        role: string;
        query?: string;
        response?: string;
        retrieved_chunks?: string[];
        timestamp: string;
      }>;
      current_retrieved_chunks: Array<{
        id: string;
        title: string;
        source: string;
        content: string;
        metadata: {
          publish_date?: string;
          effective_date?: string;
          expiration_date?: string;
          chunk_type?: string;
          confidence: number;
          retrieval_rank: number;
        };
      }>;
    };
    
    execution: {
      actual: {
        response: string;
        performance_metrics: {
          total_response_time: number;
          retrieval_time: number;
          generation_time: number;
          tokens_used: number;
          chunks_considered: number;
        };
        retrieval_quality?: {
          max_similarity: number;
          avg_similarity: number;
          diversity_score: number;
        };
        generation_info?: {
          reasoning_chain?: string;
          citation_usage?: string[];
        };
      };
      user_feedback?: {
        rating: number;
        category: string;
        comment: string;
        concern: string;
        suggested_improvement?: string;
        feedback_date: string;
        feedback_source: string;
      };
    };
    
    analysis?: {
      issue_type: string;
      root_cause: string;
      expected_answer: string;
      acceptance_criteria: string;
      quality_scores: {
        context_understanding: number;
        answer_accuracy: number;
        answer_completeness: number;
        clarity: number;
        citation_quality: number;
      };
      optimization_suggestions: string[];
      notes: string;
      analyzed_by: string;
      analysis_date: string;
    };
  };
}



1. 