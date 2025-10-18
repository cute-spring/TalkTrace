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

# 演示测试用例数据
MOCK_TEST_CASES = [
    {
        "id": "TC-0001",
        "name": "投资基金风险咨询测试用例",
        "description": "测试AI对投资基金风险问题的回答质量",
        "status": "draft",
        "owner": "expert@company.com",
        "priority": "high",
        "domain": "finance",
        "difficulty": "medium",
        "created_date": "2024-01-15T10:00:00Z",
        "tags": [{"name": "finance", "color": "#1890ff"}, {"name": "high-priority", "color": "#ff4d4f"}],
    },
    {
        "id": "TC-0002",
        "name": "AI基础概念测试用例",
        "description": "测试AI对基础概念问题的理解",
        "status": "approved",
        "owner": "developer@company.com",
        "priority": "medium",
        "domain": "technology",
        "difficulty": "easy",
        "created_date": "2024-01-15T11:00:00Z",
        "tags": [{"name": "technology", "color": "#52c41a"}],
    },
    {
        "id": "TC-0003",
        "name": "React路由配置测试用例",
        "description": "测试AI对React开发问题的解答能力",
        "status": "pending",
        "owner": "frontend@company.com",
        "priority": "medium",
        "domain": "development",
        "difficulty": "medium",
        "created_date": "2024-01-15T12:00:00Z",
        "tags": [{"name": "react", "color": "#61dafb"}, {"name": "frontend", "color": "#ff7875"}],
    },
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