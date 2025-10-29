# Talk Trace Backend (Python FastAPI)

测试样本管理平台后端服务 - Python FastAPI版本

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

复制 `.env.example` 到 `.env` 并根据需要修改配置：

```bash
cp .env.example .env
```

### 启动开发服务器

```bash
# 方式1: 使用启动脚本
python start.py

# 方式2: 直接使用uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# 方式3: 使用模块方式
python -m app.main
```

### 访问API文档

启动服务器后，可以通过以下地址访问：

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **OpenAPI JSON**: http://localhost:8001/openapi.json

## 📁 项目结构

```
backend-python/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── config.py            # 配置管理
│   ├── models/              # Pydantic数据模型
│   │   ├── __init__.py
│   │   ├── common.py        # 通用模型
│   │   ├── history.py       # 历史记录模型
│   │   ├── test_case.py     # 测试用例模型
│   │   └── import.py        # 导入任务模型
│   ├── services/            # 业务逻辑服务
│   │   ├── __init__.py
│   │   ├── history_service.py
│   │   ├── test_case_service.py
│   │   ├── import_service.py
│   │   └── demo_data.py     # 演示数据
│   ├── api/                 # API路由
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── history.py   # 历史记录路由
│   │       ├── test_cases.py
│   │       ├── import_data.py
│   │       └── analytics.py
│   ├── utils/               # 工具函数
│   │   ├── __init__.py
│   │   └── logger.py        # 日志配置
│   └── config.py            # 应用配置
├── requirements.txt         # 依赖列表
├── .env.example            # 环境变量示例
├── start.py                # 启动脚本
└── README.md
```

## 🔧 API端点

### 历史记录 (`/api/v1/history`)

- `GET /search` - 搜索历史记录
- `GET /sessions/{session_id}` - 获取会话详情
- `GET /models` - 获取可用模型列表
- `GET /health` - 健康检查

### 测试用例 (`/api/v1/test-cases`)

- `GET /` - 获取测试用例列表
- `GET /{id}` - 获取单个测试用例
- `POST /` - 创建测试用例
- `PUT /{id}` - 更新测试用例
- `DELETE /{id}` - 删除测试用例
- `POST /batch` - 批量操作
- `GET /statistics/overview` - 获取统计信息
- `GET /tags` - 获取标签列表

### 导入功能 (`/api/v1/import`)

- `POST /preview` - 预览导入数据
- `POST /execute` - 执行导入
- `GET /progress/{task_id}` - 获取导入进度
- `GET /tasks` - 获取导入任务列表
- `DELETE /tasks/{task_id}` - 删除导入任务

### 分析统计 (`/api/v1/analytics`)

- `GET /overview` - 获取概览统计
- `GET /health` - 分析服务健康检查

## 🛠️ 开发工具

### 代码格式化

```bash
pip install black
black app/
```

### 类型检查

```bash
pip install mypy
mypy app/
```

### 测试

```bash
pytest tests/
```

## 🎯 特性

- **高性能**: 基于FastAPI的异步框架
- **类型安全**: 使用Pydantic进行数据验证
- **自动文档**: 自动生成OpenAPI文档
- **结构化日志**: 使用structlog记录日志
- **数据演示**: 内置演示数据用于测试
- **CORS支持**: 支持跨域请求
- **错误处理**: 统一的错误处理机制

## 🔄 与Node.js版本的差异

| 特性 | Python FastAPI | Node.js Express |
|------|----------------|-----------------|
| **性能** | 高性能异步处理 | 高性能事件循环 |
| **类型安全** | Pydantic运行时检查 | TypeScript编译时检查 |
| **数据处理** | pandas强大的数据分析能力 | 手工处理或额外库 |
| **API文档** | 自动生成Swagger文档 | 需要额外工具 |
| **开发体验** | 优秀的IDE支持和自动补全 | 良好的IDE支持 |
| **调试** | Python调试器简单直观 | Node.js调试器 |
| **部署** | 单个Docker镜像 | 多阶段构建 |

## 📝 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `PORT` | 8001 | 服务器端口 |
| `HOST` | 0.0.0.0 | 服务器主机 |
| `ENVIRONMENT` | development | 运行环境 |
| `ALLOWED_ORIGINS` | http://localhost:3000,http://localhost:5173 | 允许的跨域来源 |
| `LOG_LEVEL` | INFO | 日志级别 |
| `LOG_FORMAT` | json | 日志格式 (json/console) |
| `BIGQUERY_USE_MOCK` | true | 是否使用Mock模式（true为使用演示数据，false为连接真实BigQuery） |
| `GCP_PROJECT_ID` | - | GCP项目ID（在BIGQUERY_USE_MOCK=false时必填） |
| `GCP_DATASET_ID` | - | BigQuery数据集ID（在BIGQUERY_USE_MOCK=false时必填） |
| `GCP_TABLE_ID` | test_cases | 可选，脚本使用的测试用例表ID |
| `GOOGLE_APPLICATION_CREDENTIALS` | ./credentials/google-credentials.json | 服务账号凭证文件路径（在BIGQUERY_USE_MOCK=false时必填） |

### BigQuery连接与启动检查
- 当 `BIGQUERY_USE_MOCK=true` 时，后端使用内置演示数据，不依赖真实BigQuery。
- 当 `BIGQUERY_USE_MOCK=false` 时，需要配置 `GCP_PROJECT_ID`、`GCP_DATASET_ID` 和 `GOOGLE_APPLICATION_CREDENTIALS`。
- 应用启动时会进行一次BigQuery连通性检查，并记录日志；若连接失败，接口将自动回退到演示数据以保证可用性。