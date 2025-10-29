"""FastAPI主应用"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import os

from app.config import settings
from app.utils.logger import logger
from app.services.history_service import HistoryService
from app.api.v1 import history, test_cases, import_data, analytics

# 创建FastAPI应用实例
app = FastAPI(
    title="Talk Trace API",
    description="测试样本管理平台后端服务 (Python FastAPI版本)",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录请求日志"""
    start_time = time.time()

    # 记录请求开始
    logger.info(
        "Request started",
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host if request.client else None
    )

    # 处理请求
    response = await call_next(request)

    # 计算处理时间
    process_time = time.time() - start_time

    # 记录请求完成
    logger.info(
        "Request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=round(process_time, 4)
    )

    # 添加处理时间到响应头
    response.headers["X-Process-Time"] = str(round(process_time, 4))

    return response

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(
        "Unhandled exception",
        method=request.method,
        url=str(request.url),
        error=str(exc),
        exc_info=True
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "服务器内部错误"
            }
        }
    )

# 根路径
@app.get("/")
async def root():
    """API根路径"""
    return {
        "success": True,
        "data": {
            "name": "Talk Trace API (Python)",
            "version": "2.0.0",
            "description": "测试样本管理平台后端服务",
            "environment": settings.environment,
            "timestamp": time.time(),
            "endpoints": {
                "docs": "/docs",
                "redoc": "/redoc",
                "openapi": "/openapi.json",
                "api": "/api/v1",
                "health": "/health"
            },
        },
    }

# 健康检查端点
@app.get("/health")
async def health_check():
    """系统健康检查"""
    from datetime import datetime

    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time(),
        "environment": settings.environment,
        "version": "2.0.0"
    }

    return {
        "success": True,
        "data": health_data
    }

# API信息端点
@app.get("/api")
async def api_info():
    """API版本信息"""
    return {
        "success": True,
        "data": {
            "version": "v1",
            "name": "Talk Trace API",
            "description": "测试样本管理平台API",
            "endpoints": {
                "history": "/api/v1/history",
                "test_cases": "/api/v1/test-cases",
                "import": "/api/v1/import",
                "analytics": "/api/v1/analytics",
            },
        },
    }

# 注册API路由
app.include_router(
    history.router,
    prefix="/api/v1/history",
    tags=["history"]
)

app.include_router(
    test_cases.router,
    prefix="/api/v1/test-cases",
    tags=["test-cases"]
)

app.include_router(
    import_data.router,
    prefix="/api/v1/import",
    tags=["import"]
)

app.include_router(
    analytics.router,
    prefix="/api/v1/analytics",
    tags=["analytics"]
)

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info(
        "Talk Trace API starting up",
        version="2.0.0",
        environment=settings.environment,
        host=settings.host,
        port=settings.port
    )

    # 在启动时执行一次 BigQuery 连通性检测
    try:
        history_service = HistoryService()
        connection_ok = await history_service.test_connection()
        logger.info(
            "BigQuery connectivity check completed",
            available=connection_ok,
            use_real_bigquery=settings.use_real_bigquery,
            project_id=settings.gcp_project_id,
            dataset_id=settings.gcp_dataset_id,
        )
    except Exception as e:
        logger.error(
            "BigQuery connectivity check failed",
            error=str(e),
            exc_info=True
        )

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("Talk Trace API shutting down")

# 如果直接运行此文件，则启动开发服务器
if __name__ == "__main__":
    import uvicorn

    logger.info(
        "Starting development server",
        host=settings.host,
        port=settings.port,
        reload=True
    )

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info"
    )