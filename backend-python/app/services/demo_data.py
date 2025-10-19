"""演示数据生成器"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

# 演示历史记录数据
MOCK_HISTORY_DATA = [
    {
        "session_id": "session_demo_001",
        "user_query": "帮我比较一下投资基金和股票投资的优缺点",
        "ai_response": "投资基金的优势包括分散风险、专业管理等...",
        "user_rating": 4,
        "model_id": "gpt-4o-mini",
        "created_at": "2024-01-15T10:00:00Z",
        "retrieval_chunks": [
            {"id": "CH-1001", "title": "投资基金基础知识", "content": "投资基金是一种集合投资工具..."},
            {"id": "CH-1002", "title": "股票投资指南", "content": "股票是公司的所有权凭证..."},
        ],
    },
    {
        "session_id": "session_demo_002",
        "user_query": "什么是人工智能？",
        "ai_response": "人工智能是计算机科学的一个分支...",
        "user_rating": 5,
        "model_id": "gpt-4o",
        "created_at": "2024-01-15T11:00:00Z",
        "retrieval_chunks": [
            {"id": "CH-2001", "title": "AI基础概念", "content": "人工智能是指让机器模拟人类智能..."},
        ],
    },
    {
        "session_id": "session_demo_003",
        "user_query": "如何配置React项目的路由？",
        "ai_response": "可以使用React Router库来配置路由...",
        "user_rating": 3,
        "model_id": "gpt-4o-mini",
        "created_at": "2024-01-15T12:00:00Z",
        "retrieval_chunks": [
            {"id": "CH-3001", "title": "React Router配置", "content": "React Router是React应用的路由库..."},
        ],
    },
    {
        "session_id": "session_demo_004",
        "user_query": "Python中装饰器是如何工作的？",
        "ai_response": "装饰器是Python中一种修改函数或类的机制...",
        "user_rating": 5,
        "model_id": "claude-3-sonnet",
        "created_at": "2024-01-15T13:00:00Z",
        "retrieval_chunks": [
            {"id": "CH-4001", "title": "Python装饰器详解", "content": "装饰器本质上是一个函数..."},
        ],
    },
    {
        "session_id": "session_demo_005",
        "user_query": "什么是微服务架构？",
        "ai_response": "微服务架构是一种将应用程序拆分为小型服务的架构风格...",
        "user_rating": 4,
        "model_id": "gpt-4o",
        "created_at": "2024-01-15T14:00:00Z",
        "retrieval_chunks": [
            {"id": "CH-5001", "title": "微服务架构原理", "content": "微服务架构提倡将单一应用程序..."},
        ],
    },
]

# 演示测试用例数据 - 完整结构
MOCK_TEST_CASES = [
    {
        "id": "TC-0001",
        "name": "投资基金风险咨询测试用例",
        "description": "测试AI对投资基金风险问题的回答质量和上下文理解能力",
        "metadata": {
            "status": "draft",
            "owner": "expert@company.com",
            "priority": "high",
            "tags": [{"name": "finance", "color": "#1890ff"}, {"name": "high-priority", "color": "#ff4d4f"}, {"name": "multi-turn", "color": "#722ed1"}],
            "version": "1.0",
            "created_date": "2024-01-15T10:00:00Z",
            "updated_date": "2024-01-16T15:30:00Z",
            "source_session": "session_demo_001"
        },
        "domain": "finance",
        "difficulty": "medium",
        "test_config": {
            "model": {
                "name": "gpt-4o-mini",
                "version": "2024-01-01",
                "params": {
                    "temperature": 0.0,
                    "max_tokens": 512,
                    "top_p": 0.9
                }
            },
            "prompts": {
                "system": "You are a helpful assistant specialized in financial advice. Always provide accurate, clear, and actionable information.",
                "user_instruction": "Using the provided documents, answer the user's question comprehensively and cite your sources."
            },
            "retrieval": {
                "top_k": 5,
                "similarity_threshold": 0.7,
                "reranker_enabled": True
            }
        },
        "input": {
            "current_query": {
                "text": "能再解释一下第一个方案的具体风险吗？",
                "timestamp": "2024-01-15T10:02:00Z"
            },
            "conversation_history": [
                {
                    "turn": 1,
                    "role": "user",
                    "query": "帮我比较一下投资基金和股票投资的优缺点",
                    "timestamp": "2024-01-15T10:00:00Z"
                },
                {
                    "turn": 2,
                    "role": "assistant",
                    "response": "投资基金的优势包括分散风险、专业管理、门槛较低等。缺点包括管理费用、收益可能低于直接投资等。股票投资的优势是收益潜力大、控制权强，缺点是风险集中、需要专业知识等。",
                    "retrieved_chunks": ["CH-1001", "CH-1002"],
                    "timestamp": "2024-01-15T10:00:01Z"
                }
            ],
            "current_retrieved_chunks": [
                {
                    "id": "CH-1005",
                    "title": "投资基金风险管理指南",
                    "source": "https://internal.com/finance/fund-risk",
                    "content": "投资基金的具体风险包括：1. 市场风险：基金净值随市场波动 2. 流动性风险：某些基金可能难以及时赎回 3. 管理风险：基金经理决策失误 4. 信用风险：债券基金可能面临违约 5. 运营风险：基金公司运作问题",
                    "metadata": {
                        "publish_date": "2023-06-01",
                        "effective_date": "2023-06-01",
                        "expiration_date": "2024-12-31",
                        "chunk_type": "conceptual",
                        "confidence": 0.92,
                        "retrieval_rank": 1
                    }
                }
            ]
        },
        "execution": {
            "actual": {
                "response": "投资基金的具体风险包括市场风险、流动性风险、管理风险、信用风险和运营风险。市场风险是指基金净值会随着整个市场的波动而变化...",
                "performance_metrics": {
                    "total_response_time": 2.1,
                    "retrieval_time": 0.3,
                    "generation_time": 1.8,
                    "tokens_used": 345,
                    "chunks_considered": 5
                },
                "retrieval_quality": {
                    "max_similarity": 0.92,
                    "avg_similarity": 0.78,
                    "diversity_score": 0.65
                }
            },
            "user_feedback": {
                "rating": 3,
                "category": "accuracy",
                "comment": "回答列出了风险类型，但没有具体说明如何识别和应对这些风险",
                "concern": "感觉回答比较模板化，缺乏针对性的建议",
                "suggested_improvement": "希望能举例说明每种风险在什么情况下会发生",
                "feedback_date": "2024-01-15T10:02:30Z",
                "feedback_source": "user"
            }
        },
        "analysis": {
            "issue_type": "context_understanding",
            "root_cause": "未能正确解析'第一个方案'在对话历史中的指代，用户询问的是投资基金的风险，但AI回答过于泛化",
            "expected_answer": "您询问的'第一个方案'（投资基金）的具体风险包括：1. 市场风险：基金净值会随股市波动 2. 流动性风险：某些基金赎回受限 3. 管理风险：依赖基金经理能力 4. 费用风险：管理费侵蚀收益 5. 集中度风险：投资组合过于集中...",
            "acceptance_criteria": "1. 必须正确识别'第一个方案'指代投资基金 2. 需要结合用户提到的具体场景 3. 提供具体的风险识别方法 4. 给出实用的风险应对建议 5. 引用相关的文档来源",
            "quality_scores": {
                "context_understanding": 2,
                "answer_accuracy": 4,
                "answer_completeness": 3,
                "clarity": 3,
                "citation_quality": 4
            },
            "optimization_suggestions": [
                "改进对话状态跟踪，准确识别历史指代",
                "在回答中增加具体示例提高实用性",
                "加强上下文相关的检索策略"
            ],
            "notes": "用户明显在延续之前的对话，但AI未能充分理解上下文。需要提升指代消解能力。",
            "analyzed_by": "expert@company.com",
            "analysis_date": "2024-01-16T15:30:00Z"
        }
    },
    {
        "id": "TC-0002",
        "name": "React路由配置测试用例",
        "description": "测试AI对React开发问题的解答能力和代码示例质量",
        "metadata": {
            "status": "approved",
            "owner": "frontend@company.com",
            "priority": "medium",
            "tags": [{"name": "react", "color": "#61dafb"}, {"name": "frontend", "color": "#ff7875"}, {"name": "code-example", "color": "#52c41a"}],
            "version": "2.0",
            "created_date": "2024-01-15T11:00:00Z",
            "updated_date": "2024-01-17T09:15:00Z",
            "source_session": "session_demo_002"
        },
        "domain": "development",
        "difficulty": "medium",
        "test_config": {
            "model": {
                "name": "gpt-4o",
                "version": "2024-01-01",
                "params": {
                    "temperature": 0.1,
                    "max_tokens": 800,
                    "top_p": 0.95
                }
            },
            "prompts": {
                "system": "You are an expert React developer. Provide clear, accurate code examples and explain best practices.",
                "user_instruction": "Answer the user's React question with working code examples and explain the concepts clearly."
            },
            "retrieval": {
                "top_k": 3,
                "similarity_threshold": 0.8,
                "reranker_enabled": True
            }
        },
        "input": {
            "current_query": {
                "text": "如何配置React项目的路由？",
                "timestamp": "2024-01-15T11:00:00Z"
            },
            "conversation_history": [],
            "current_retrieved_chunks": [
                {
                    "id": "CH-3001",
                    "title": "React Router配置指南",
                    "source": "https://docs.react-router.com",
                    "content": "React Router是React应用的标准路由库。安装命令：npm install react-router-dom@6。基本配置包括创建BrowserRouter、定义Routes和Route组件...",
                    "metadata": {
                        "publish_date": "2023-12-01",
                        "effective_date": "2023-12-01",
                        "chunk_type": "tutorial",
                        "confidence": 0.95,
                        "retrieval_rank": 1
                    }
                }
            ]
        },
        "execution": {
            "actual": {
                "response": "配置React项目路由需要使用React Router库。首先安装：npm install react-router-dom@6。然后在应用中配置路由：\n\n```jsx\nimport { BrowserRouter, Routes, Route } from 'react-router-dom';\nimport Home from './pages/Home';\nimport About from './pages/About';\n\nfunction App() {\n  return (\n    <BrowserRouter>\n      <Routes>\n        <Route path=\"/\" element={<Home />} />\n        <Route path=\"/about\" element={<About />} />\n      </Routes>\n    </BrowserRouter>\n  );\n}\n```",
                "performance_metrics": {
                    "total_response_time": 1.8,
                    "retrieval_time": 0.2,
                    "generation_time": 1.6,
                    "tokens_used": 287,
                    "chunks_considered": 3
                },
                "retrieval_quality": {
                    "max_similarity": 0.95,
                    "avg_similarity": 0.85,
                    "diversity_score": 0.72
                }
            }
        },
        "analysis": {
            "issue_type": "good_example",
            "root_cause": "回答准确、代码示例完整、解释清晰",
            "expected_answer": "提供了准确的React Router配置方法和完整的代码示例",
            "acceptance_criteria": "1. 提供正确的安装命令 2. 包含完整的路由配置代码 3. 代码示例可运行 4. 解释清楚各个组件的作用",
            "quality_scores": {
                "context_understanding": 5,
                "answer_accuracy": 5,
                "answer_completeness": 4,
                "clarity": 5,
                "citation_quality": 4
            },
            "optimization_suggestions": [
                "可以添加更多高级用法示例",
                "包含嵌套路由的配置方法"
            ],
            "notes": "这是一个质量较好的回答，代码示例完整且正确。",
            "analyzed_by": "frontend@company.com",
            "analysis_date": "2024-01-17T09:15:00Z"
        }
    }
]

# 可用模型列表
AVAILABLE_MODELS = ["gpt-4o-mini", "gpt-4o", "claude-3-sonnet"]

def generate_more_history_data(count: int = 20) -> List[Dict[str, Any]]:
    """生成更多历史记录数据用于测试"""
    base_time = datetime.now() - timedelta(days=7)
    topics = [
        "机器学习算法原理", "数据库优化技巧", "前端性能优化", "云计算服务比较",
        "网络安全最佳实践", "移动开发框架选择", "API设计原则", "代码重构方法",
        "项目管理工具", "DevOps实践指南"
    ]

    models = AVAILABLE_MODELS

    data = []
    for i in range(count):
        session_time = base_time + timedelta(hours=random.randint(0, 168))
        topic = random.choice(topics)
        model = random.choice(models)

        data.append({
            "session_id": f"session_gen_{i+1:04d}",
            "user_query": f"请详细解释{topic}",
            "ai_response": f"关于{topic}，这是一个很好的问题。让我为您详细解释...",
            "user_rating": random.randint(1, 5),
            "model_id": model,
            "created_at": session_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "retrieval_chunks": [
                {"id": f"CH-{i+1:04d}-1", "title": f"{topic}基础", "content": f"{topic}的基础知识..."},
            ],
        })

    return data