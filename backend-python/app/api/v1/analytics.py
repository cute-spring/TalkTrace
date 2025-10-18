"""分析API路由"""
from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, timedelta
from typing import Optional

from app.services.history_service import HistoryService
from app.services.test_case_service import TestCaseService
from app.models.common import ApiResponse
from app.utils.logger import logger

router = APIRouter()
history_service = HistoryService()
test_case_service = TestCaseService()

@router.get("/overview", response_model=ApiResponse[dict])
async def get_overview(
    start_date: Optional[str] = Query(None, description="开始日期 (ISO格式)"),
    end_date: Optional[str] = Query(None, description="结束日期 (ISO格式)")
):
    """获取概览统计信息"""
    try:
        # 默认查询最近7天的数据
        if not end_date:
            end_date = datetime.now().isoformat()
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).isoformat()

        # 获取历史记录统计
        from app.models.history import HistorySearchRequest
        search_request = HistorySearchRequest(
            start_time=datetime.fromisoformat(start_date.replace('Z', '+00:00')),
            end_time=datetime.fromisoformat(end_date.replace('Z', '+00:00')),
            page=1,
            page_size=1
        )
        history_stats = await history_service.search_history(search_request)

        # 获取测试用例统计
        test_case_stats = await test_case_service.get_statistics()

        # 获取模型统计
        models = await history_service.get_model_ids()

        # 组合统计数据
        overview_data = {
            "history": {
                "total_sessions": history_stats["total"],
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date
                }
            },
            "test_cases": test_case_stats,
            "models": {
                "total_count": len(models),
                "available_models": models
            },
            "generated_at": datetime.now().isoformat() + "Z"
        }

        logger.info("Overview statistics retrieved",
                   history_total=overview_data["history"]["total_sessions"],
                   test_case_total=overview_data["test_cases"]["total_count"],
                   model_count=overview_data["models"]["total_count"])

        return ApiResponse(success=True, data=overview_data)

    except Exception as e:
        logger.error("Get overview failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="获取概览统计失败"
        )

@router.get("/health", response_model=ApiResponse[dict])
async def get_analytics_health():
    """检查分析服务健康状态"""
    try:
        # 检查各个服务的连接状态
        history_healthy = await history_service.test_connection()

        # 获取基本统计信息
        test_case_stats = await test_case_service.get_statistics()
        models = await history_service.get_model_ids()

        health_data = {
            "status": "healthy" if history_healthy else "degraded",
            "services": {
                "history_service": "healthy" if history_healthy else "unhealthy",
                "test_case_service": "healthy"
            },
            "statistics": {
                "history_records_available": history_healthy,
                "test_cases_count": test_case_stats["total_count"],
                "models_count": len(models)
            },
            "timestamp": datetime.now().isoformat() + "Z"
        }

        logger.info("Analytics health check completed",
                   overall_status=health_data["status"],
                   history_healthy=history_healthy)

        return ApiResponse(
            success=history_healthy,
            data=health_data
        )

    except Exception as e:
        logger.error("Analytics health check failed", error=str(e))
        return ApiResponse(
            success=False,
            data={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat() + "Z"
            }
        )