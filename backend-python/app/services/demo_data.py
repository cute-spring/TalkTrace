"""演示数据生成器"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random
import json
from pathlib import Path

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
            {
                "id": "CH-1001",
                "title": "投资基金基础知识",
                "source": "https://internal.com/finance/fund-basics",
                "content": "投资基金是一种集合投资工具，通过专业基金经理管理资金，投资于多种证券组合。",
                "metadata": {
                    "publish_date": "2023-06-01",
                    "effective_date": "2023-06-01",
                    "expiration_date": "2024-12-31",
                    "chunk_type": "conceptual",
                    "confidence": 0.89,
                    "retrieval_rank": 1
                }
            },
            {
                "id": "CH-1002",
                "title": "股票投资指南",
                "source": "https://internal.com/finance/stock-guide",
                "content": "股票是公司的所有权凭证，代表投资者对公司的部分所有权，可以分享公司利润。",
                "metadata": {
                    "publish_date": "2023-06-15",
                    "effective_date": "2023-06-15",
                    "expiration_date": "2024-12-31",
                    "chunk_type": "guide",
                    "confidence": 0.85,
                    "retrieval_rank": 2
                }
            },
        ],
        "test_config": {
            "model": {
                "name": "gpt-4o-mini",
                "params": {
                    "temperature": 0.0,
                    "max_tokens": 512
                }
            },
            "prompts": {
                "system": {
                    "version": "v1.2.0",
                    "content": "You are a helpful assistant specializing in financial advice. Always provide accurate, clear, and actionable information."
                },
                "user_instruction": {
                    "role": "Financial Advisor",
                    "version": "v1.1.0",
                    "content": "Using the provided documents, answer the user's financial question comprehensively and cite your sources."
                }
            }
        }
    },
    {
        "session_id": "session_demo_002",
        "user_query": "什么是人工智能？",
        "ai_response": "人工智能是计算机科学的一个分支...",
        "user_rating": 5,
        "model_id": "gpt-4o",
        "created_at": "2024-01-15T11:00:00Z",
        "retrieval_chunks": [
            {
                "id": "CH-2001",
                "title": "AI基础概念",
                "source": "https://internal.com/tech/ai-basics",
                "content": "人工智能是指让机器模拟人类智能，执行通常需要人类智能的任务。",
                "metadata": {
                    "publish_date": "2023-07-01",
                    "effective_date": "2023-07-01",
                    "expiration_date": "2025-06-30",
                    "chunk_type": "conceptual",
                    "confidence": 0.91,
                    "retrieval_rank": 1
                }
            },
        ],
        "test_config": {
            "model": {
                "name": "gpt-4o",
                "params": {
                    "temperature": 0.1,
                    "max_tokens": 700
                }
            },
            "prompts": {
                "system": {
                    "version": "v1.8.0",
                    "content": "You are an AI expert specializing in artificial intelligence concepts and applications. Provide clear, educational explanations."
                },
                "user_instruction": {
                    "role": "AI Educator",
                    "version": "v1.2.1",
                    "content": "Explain AI concepts in simple terms with practical examples that help users understand the technology better."
                }
            }
        }
    },
    {
        "session_id": "session_demo_003",
        "user_query": "如何配置React项目的路由？",
        "ai_response": "可以使用React Router库来配置路由...",
        "user_rating": 3,
        "model_id": "gpt-4o-mini",
        "created_at": "2024-01-15T12:00:00Z",
        "retrieval_chunks": [
            {
                "id": "CH-3001",
                "title": "React Router配置",
                "source": "https://docs.react-router.com",
                "content": "React Router是React应用的标准路由库，安装命令：npm install react-router-dom@6。",
                "metadata": {
                    "publish_date": "2023-12-01",
                    "effective_date": "2023-12-01",
                    "expiration_date": "2024-12-31",
                    "chunk_type": "tutorial",
                    "confidence": 0.95,
                    "retrieval_rank": 1
                }
            },
        ],
        "test_config": {
            "model": {
                "name": "gpt-4o-mini",
                "params": {
                    "temperature": 0.1,
                    "max_tokens": 600
                }
            },
            "prompts": {
                "system": {
                    "version": "v2.0.1",
                    "content": "You are a helpful assistant specializing in React development. Provide clear, practical code examples and best practices."
                },
                "user_instruction": {
                    "role": "React Developer",
                    "version": "v1.3.2",
                    "content": "Using the provided documentation, answer the user's React question with working code examples and explain the concepts clearly."
                }
            }
        }
    },
    {
        "session_id": "session_demo_004",
        "user_query": "Python中装饰器是如何工作的？",
        "ai_response": "装饰器是Python中一种修改函数或类的机制...",
        "user_rating": 5,
        "model_id": "claude-3-sonnet",
        "created_at": "2024-01-15T13:00:00Z",
        "retrieval_chunks": [
            {
                "id": "CH-4001",
                "title": "Python装饰器详解",
                "source": "https://internal.com/tech/python-decorators",
                "content": "装饰器本质上是一个函数，它接受另一个函数作为参数并返回一个新的函数。",
                "metadata": {
                    "publish_date": "2023-08-15",
                    "effective_date": "2023-08-15",
                    "expiration_date": "2025-08-15",
                    "chunk_type": "tutorial",
                    "confidence": 0.88,
                    "retrieval_rank": 1
                }
            },
        ],
        "test_config": {
            "model": {
                "name": "claude-3-sonnet",
                "params": {
                    "temperature": 0.2,
                    "max_tokens": 768
                }
            },
            "prompts": {
                "system": {
                    "version": "v1.5.2",
                    "content": "You are Claude, an AI assistant with deep knowledge of Python programming and software architecture."
                },
                "user_instruction": {
                    "role": "Python Instructor",
                    "version": "v2.1.0",
                    "content": "Based on the documentation and context provided, give a detailed explanation with code examples and best practices."
                }
            }
        }
    },
    {
        "session_id": "session_demo_005",
        "user_query": "什么是微服务架构？",
        "ai_response": "微服务架构是一种将应用程序拆分为小型服务的架构风格...",
        "user_rating": 4,
        "model_id": "gpt-4o",
        "created_at": "2024-01-15T14:00:00Z",
        "retrieval_chunks": [
            {
                "id": "CH-5001",
                "title": "微服务架构原理",
                "source": "https://internal.com/tech/microservices-principles",
                "content": "微服务架构提倡将单一应用程序拆分为一组小型服务，每个服务运行在自己的进程中，服务之间通过轻量级通信机制进行通信。",
                "metadata": {
                    "publish_date": "2023-09-01",
                    "effective_date": "2023-09-01",
                    "expiration_date": "2025-09-01",
                    "chunk_type": "architectural",
                    "confidence": 0.87,
                    "retrieval_rank": 1
                }
            },
        ],
        "test_config": {
            "model": {
                "name": "gpt-4o",
                "params": {
                    "temperature": 0.3,
                    "max_tokens": 800
                }
            },
            "prompts": {
                "system": {
                    "version": "v2.1.0",
                    "content": "You are an expert software architect specializing in distributed systems and microservices design."
                },
                "user_instruction": {
                    "role": "System Architect",
                    "version": "v1.4.1",
                    "content": "Provide comprehensive explanations of architectural concepts with real-world examples and best practices."
                }
            }
        }
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
    },
    {
        "id": "TC-0003",
        "name": "测试用例1",
        "description": "完整的测试用例示例，包含所有必要字段",
        "metadata": {
            "status": "draft",
            "owner": "user@example.com",
            "priority": "medium",
            "tags": [{"name": "finance", "color": "#1890ff"}, {"name": "multi-turn", "color": "#722ed1"}],
            "version": "1.0",
            "created_date": "2024-01-15T00:00:00Z",
            "updated_date": "2024-01-16T00:00:00Z",
            "source_session": "session_123"
        },
        "domain": "finance",
        "difficulty": "medium",
        "test_config": {
            "model": {
                "name": "gpt-4o-mini",
                "params": {
                    "temperature": 0.0,
                    "max_tokens": 512
                }
            },
            "prompts": {
                "system": "You are a helpful assistant specializing in financial advice. Always provide accurate, clear, and actionable information.",
                "user_instruction": "Using the provided documents, answer the user's question comprehensively and cite your sources."
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
                    "response": "投资基金的优势包括...",
                    "retrieved_chunks": ["CH-1001", "CH-1002"],
                    "timestamp": "2024-01-15T10:00:01Z"
                }
            ],
            "current_retrieved_chunks": [
                {
                    "id": "CH-1005",
                    "title": "投资基金风险管理指南",
                    "source": "https://internal.com/finance/fund-risk",
                    "content": "投资基金的具体风险包括：...",
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
                "response": "投资基金的具体风险包括市场风险...",
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
                "feedback_date": "2024-01-15T10:02:00Z",
                "feedback_source": "user"
            }
        },
        "analysis": {
            "issue_type": "context_understanding",
            "root_cause": "未能正确解析'第一个方案'在对话历史中的指代",
            "expected_answer": "您询问的'第一个方案'（投资基金）的具体风险包括：...",
            "acceptance_criteria": "1. 必须正确识别'第一个方案'指代投资基金...",
            "quality_scores": {
                "context_understanding": 2,
                "answer_accuracy": 4,
                "answer_completeness": 3,
                "clarity": 3,
                "citation_quality": 4
            },
            "optimization_suggestions": [
                "改进对话状态跟踪，准确识别历史指代",
                "在回答中增加具体示例提高实用性"
            ],
            "notes": "用户明显在延续之前的对话，但AI未能充分理解上下文。",
            "analyzed_by": "expert@company.com",
            "analysis_date": "2024-01-16"
        }
    }
]

# 从JSON文件加载测试用例（如果存在），保持API契约不变
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def _load_json_list(filename: str) -> List[Dict[str, Any]]:
    path = DATA_DIR / filename
    if path.exists():
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except Exception:
            pass
    return []

_loaded_cases = _load_json_list("mock_test_cases.json")
if _loaded_cases:
    MOCK_TEST_CASES = _loaded_cases

# 可用模型列表
AVAILABLE_MODELS = ["gpt-4o-mini", "gpt-4o", "claude-3-sonnet"]

# 主题特定的测试配置模板
TOPIC_TEST_CONFIGS = {
    "机器学习算法原理": {
        "model": {"name": "gpt-4o", "params": {"temperature": 0.2, "max_tokens": 800}},
        "prompts": {
            "system": {
                "version": "v1.5.0",
                "content": "You are an expert machine learning engineer specializing in algorithms, neural networks, and AI systems design. Provide comprehensive, technically accurate explanations with practical examples."
            },
            "user_instruction": {
                "role": "ML Engineer",
                "version": "v1.3.0",
                "content": "Explain machine learning concepts with clear technical depth, mathematical intuition, and real-world applications. Include algorithm types and use cases."
            }
        }
    },
    "数据库优化技巧": {
        "model": {"name": "gpt-4o-mini", "params": {"temperature": 0.1, "max_tokens": 700}},
        "prompts": {
            "system": {
                "version": "v1.8.0",
                "content": "You are a senior database administrator with expertise in query optimization, indexing strategies, and performance tuning. Provide practical, actionable advice for database performance."
            },
            "user_instruction": {
                "role": "Database Administrator",
                "version": "v1.2.0",
                "content": "Provide detailed database optimization techniques with specific examples, best practices, and measurable performance improvements. Focus on real-world scenarios."
            }
        }
    },
    "前端性能优化": {
        "model": {"name": "gpt-4o", "params": {"temperature": 0.1, "max_tokens": 750}},
        "prompts": {
            "system": {
                "version": "v2.0.1",
                "content": "You are a frontend performance optimization expert specializing in modern web technologies, browser rendering, and user experience optimization."
            },
            "user_instruction": {
                "role": "Performance Engineer",
                "version": "v1.4.0",
                "content": "Provide comprehensive frontend optimization strategies with code examples, performance metrics, and implementation guidelines. Focus on practical improvements."
            }
        }
    },
    "云计算服务比较": {
        "model": {"name": "claude-3-sonnet", "params": {"temperature": 0.2, "max_tokens": 900}},
        "prompts": {
            "system": {
                "version": "v1.7.0",
                "content": "You are a cloud solutions architect with extensive experience across AWS, Azure, and Google Cloud platforms. Provide balanced, vendor-neutral comparisons and recommendations."
            },
            "user_instruction": {
                "role": "Cloud Architect",
                "version": "v1.3.5",
                "content": "Provide detailed cloud service comparisons with specific use cases, cost considerations, and migration strategies. Include pros and cons of each platform."
            }
        }
    },
    "网络安全最佳实践": {
        "model": {"name": "gpt-4o", "params": {"temperature": 0.0, "max_tokens": 800}},
        "prompts": {
            "system": {
                "version": "v2.1.0",
                "content": "You are a cybersecurity specialist with expertise in enterprise security, threat detection, and compliance frameworks. Provide authoritative, security-focused guidance."
            },
            "user_instruction": {
                "role": "Security Specialist",
                "version": "v1.6.0",
                "content": "Provide comprehensive security best practices with specific implementation steps, risk assessments, and compliance considerations. Focus on practical defense strategies."
            }
        }
    },
    "移动开发框架选择": {
        "model": {"name": "gpt-4o-mini", "params": {"temperature": 0.2, "max_tokens": 650}},
        "prompts": {
            "system": {
                "version": "v1.4.0",
                "content": "You are a mobile development expert with experience in React Native, Flutter, Swift, and Kotlin development. Provide framework recommendations based on project requirements."
            },
            "user_instruction": {
                "role": "Mobile Developer",
                "version": "v1.2.5",
                "content": "Provide detailed mobile framework comparisons with performance benchmarks, development considerations, and platform-specific recommendations. Include real project examples."
            }
        }
    },
    "API设计原则": {
        "model": {"name": "gpt-4o", "params": {"temperature": 0.1, "max_tokens": 700}},
        "prompts": {
            "system": {
                "version": "v1.9.0",
                "content": "You are an API architect specializing in RESTful design, GraphQL, and enterprise API governance. Provide clear, standards-compliant API design guidance."
            },
            "user_instruction": {
                "role": "API Architect",
                "version": "v1.4.2",
                "content": "Provide comprehensive API design principles with specific examples, versioning strategies, and best practices for scalable, maintainable APIs."
            }
        }
    },
    "代码重构方法": {
        "model": {"name": "claude-3-sonnet", "params": {"temperature": 0.15, "max_tokens": 750}},
        "prompts": {
            "system": {
                "version": "v1.6.0",
                "content": "You are a senior software engineer specializing in code quality, design patterns, and refactoring techniques. Provide practical guidance for improving code maintainability."
            },
            "user_instruction": {
                "role": "Senior Engineer",
                "version": "v1.3.0",
                "content": "Provide detailed refactoring methods with before/after code examples, design pattern applications, and testing strategies. Focus on safe, incremental improvements."
            }
        }
    },
    "项目管理工具": {
        "model": {"name": "gpt-4o-mini", "params": {"temperature": 0.2, "max_tokens": 600}},
        "prompts": {
            "system": {
                "version": "v1.3.0",
                "content": "You are a project management expert with experience in agile methodologies, team collaboration, and tool selection. Provide practical advice for project workflow optimization."
            },
            "user_instruction": {
                "role": "Project Manager",
                "version": "v1.1.5",
                "content": "Provide comprehensive project management tool comparisons with team size considerations, workflow integration, and implementation best practices."
            }
        }
    },
    "DevOps实践指南": {
        "model": {"name": "claude-3-sonnet", "params": {"temperature": 0.1, "max_tokens": 850}},
        "prompts": {
            "system": {
                "version": "v2.0.0",
                "content": "You are a DevOps engineer with expertise in CI/CD pipelines, infrastructure as code, and DevOps culture transformation. Provide comprehensive implementation guidance."
            },
            "user_instruction": {
                "role": "DevOps Engineer",
                "version": "v1.5.0",
                "content": "Provide detailed DevOps implementation guides with specific tool recommendations, pipeline configurations, and organizational change strategies. Focus on practical adoption."
            }
        }
    }
}

# 主题映射到完整的检索片段信息
TOPIC_MAPPINGS = {
    "机器学习算法原理": {
        "source": "https://internal.com/tech/ml-algorithms",
        "chunk_type": "conceptual",
        "content": "机器学习算法是人工智能的核心，包括监督学习、无监督学习和强化学习等主要类型。监督学习使用标记数据训练模型，无监督学习发现数据模式，强化学习通过试错学习最优策略。",
        "publish_date": "2023-08-15",
        "effective_date": "2023-08-15",
        "expiration_date": "2025-08-15"
    },
    "数据库优化技巧": {
        "source": "https://internal.com/tech/database-optimization",
        "chunk_type": "guide",
        "content": "数据库优化技巧包括索引优化、查询优化、表结构设计和硬件配置等方面。合理创建索引可以显著提升查询性能，避免全表扫描。查询优化需要理解执行计划，减少不必要的连接和子查询。",
        "publish_date": "2023-07-20",
        "effective_date": "2023-07-20",
        "expiration_date": "2025-07-20"
    },
    "前端性能优化": {
        "source": "https://internal.com/tech/frontend-performance",
        "chunk_type": "tutorial",
        "content": "前端性能优化包括代码压缩、资源合并、懒加载、缓存策略等技术。通过减少HTTP请求、压缩静态资源、使用CDN等方式可以显著提升页面加载速度和用户体验。",
        "publish_date": "2023-09-10",
        "effective_date": "2023-09-10",
        "expiration_date": "2025-09-10"
    },
    "云计算服务比较": {
        "source": "https://internal.com/tech/cloud-comparison",
        "chunk_type": "analysis",
        "content": "云计算服务主要包括IaaS、PaaS、SaaS三种模式。AWS、Azure、Google Cloud是主要服务商，各有优势。AWS服务最全面，Azure企业集成好，Google Cloud在AI和数据分析方面领先。",
        "publish_date": "2023-10-05",
        "effective_date": "2023-10-05",
        "expiration_date": "2025-10-05"
    },
    "网络安全最佳实践": {
        "source": "https://internal.com/tech/security-practices",
        "chunk_type": "guide",
        "content": "网络安全最佳实践包括使用强密码、多因素认证、定期更新软件、网络隔离、数据加密等措施。企业需要建立完整的安全体系，包括预防、检测、响应和恢复四个环节。",
        "publish_date": "2023-06-15",
        "effective_date": "2023-06-15",
        "expiration_date": "2025-06-15"
    },
    "移动开发框架选择": {
        "source": "https://internal.com/tech/mobile-frameworks",
        "chunk_type": "comparison",
        "content": "移动开发框架选择需要考虑性能、开发效率、维护成本等因素。React Native适合跨平台开发，Flutter性能优异，原生开发体验最佳。需要根据项目需求和团队技术栈选择合适的框架。",
        "publish_date": "2023-11-20",
        "effective_date": "2023-11-20",
        "expiration_date": "2025-11-20"
    },
    "API设计原则": {
        "source": "https://internal.com/tech/api-design",
        "chunk_type": "conceptual",
        "content": "API设计原则包括RESTful设计、版本控制、错误处理、安全认证、限流熔断等方面。好的API应该简洁、一致、可靠，并提供清晰的文档和错误信息。",
        "publish_date": "2023-08-01",
        "effective_date": "2023-08-01",
        "expiration_date": "2025-08-01"
    },
    "代码重构方法": {
        "source": "https://internal.com/tech/refactoring-methods",
        "chunk_type": "tutorial",
        "content": "代码重构方法包括提取函数、重构类、优化算法、消除重复代码等。重构应该保持功能不变，改善代码结构和可读性。需要充分测试确保重构不引入新的bug。",
        "publish_date": "2023-09-25",
        "effective_date": "2023-09-25",
        "expiration_date": "2025-09-25"
    },
    "项目管理工具": {
        "source": "https://internal.com/tech/project-management-tools",
        "chunk_type": "comparison",
        "content": "项目管理工具包括Jira、Trello、Asana、Monday等。Jira功能强大适合敏捷开发，Trello简单直观适合小型项目，Asana协作功能突出。选择工具需要考虑团队规模、项目复杂度和预算等因素。",
        "publish_date": "2023-07-10",
        "effective_date": "2023-07-10",
        "expiration_date": "2025-07-10"
    },
    "DevOps实践指南": {
        "source": "https://internal.com/tech/devops-guide",
        "chunk_type": "guide",
        "content": "DevOps实践指南包括持续集成、持续部署、基础设施即代码、监控告警等核心实践。通过自动化工具链和标准化流程，提高软件交付速度和质量，促进开发和运维协作。",
        "publish_date": "2023-10-15",
        "effective_date": "2023-10-15",
        "expiration_date": "2025-10-15"
    }
}

def generate_more_history_data(count: int = 20) -> List[Dict[str, Any]]:
    """生成更多历史记录数据用于测试"""
    base_time = datetime.now() - timedelta(days=7)
    topics = list(TOPIC_MAPPINGS.keys())
    models = AVAILABLE_MODELS

    data = []
    for i in range(count):
        session_time = base_time + timedelta(hours=random.randint(0, 168))
        topic = random.choice(topics)
        model = random.choice(models)
        topic_info = TOPIC_MAPPINGS[topic]
        test_config = TOPIC_TEST_CONFIGS[topic]
        confidence = round(random.uniform(0.80, 0.96), 2)

        # Add some variation to model parameters for realism
        model_config = test_config["model"].copy()
        model_config["params"] = model_config["params"].copy()
        model_config["params"]["temperature"] = round(model_config["params"]["temperature"] + random.uniform(-0.05, 0.05), 2)
        model_config["params"]["max_tokens"] = model_config["params"]["max_tokens"] + random.randint(-100, 100)

        data.append({
            "session_id": f"session_gen_{i+1:04d}",
            "user_query": f"请详细解释{topic}",
            "ai_response": f"关于{topic}，这是一个很好的问题。让我为您详细解释...",
            "user_rating": random.randint(1, 5),
            "model_id": model_config["name"],
            "created_at": session_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "retrieval_chunks": [
                {
                    "id": f"CH-{i+1:04d}-1",
                    "title": f"{topic}详解",
                    "source": topic_info["source"],
                    "content": topic_info["content"],
                    "metadata": {
                        "publish_date": topic_info["publish_date"],
                        "effective_date": topic_info["effective_date"],
                        "expiration_date": topic_info["expiration_date"],
                        "chunk_type": topic_info["chunk_type"],
                        "confidence": confidence,
                        "retrieval_rank": 1
                    }
                },
            ],
            "test_config": {
                "model": model_config,
                "prompts": test_config["prompts"]
            }
        })

    return data