"""历史记录API路由"""
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from datetime import datetime
import json
import math

from app.services.history_service import HistoryService
from app.models.history import HistorySearchRequest, SessionDetail
from app.models.common import ApiResponse, HealthCheck
from app.utils.logger import logger

router = APIRouter()
history_service = HistoryService()

def clean_data_for_json_serialization(data):
    """清理数据以确保JSON序列化成功"""
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            cleaned[key] = clean_data_for_json_serialization(value)
        return cleaned
    elif isinstance(data, list):
        return [clean_data_for_json_serialization(item) for item in data]
    elif isinstance(data, float):
        # 处理无效的float值
        if math.isnan(data):
            return None
        elif math.isinf(data):
            return None
        else:
            return data
    elif hasattr(data, '__dict__'):
        # 处理Pydantic模型或其他对象
        return clean_data_for_json_serialization(data.__dict__)
    else:
        return data

@router.get("/search", response_model=ApiResponse[dict])
async def search_history(
    startTime: str = Query(..., description="开始时间 (ISO格式)"),
    endTime: str = Query(..., description="结束时间 (ISO格式)"),
    modelIds: Optional[List[str]] = Query(None, alias="modelIds", description="模型ID列表"),
    ratingRange: Optional[str] = Query(None, alias="ratingRange", description="评分范围，格式: '1,3'"),
    keywords: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    pageSize: int = Query(20, ge=1, le=100, alias="pageSize", description="每页大小")
):
    """搜索历史记录"""
    try:
        # 解析时间
        start_dt = datetime.fromisoformat(startTime.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(endTime.replace('Z', '+00:00'))

        # 解析评分范围
        parsed_rating_range = None
        if ratingRange:
            try:
                min_rating, max_rating = map(int, ratingRange.split(','))
                parsed_rating_range = (min_rating, max_rating)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="评分范围格式错误，应为 'min,max' 格式，例如 '1,3'"
                )

        # 创建搜索请求
        request = HistorySearchRequest(
            start_time=start_dt,
            end_time=end_dt,
            model_ids=modelIds,
            rating_range=parsed_rating_range,
            keywords=keywords,
            page=page,
            page_size=pageSize
        )

        # 执行搜索
        result = await history_service.search_history(request)

        logger.info("History search API called successfully",
                   page=page,
                   page_size=pageSize,
                   results_count=len(result["items"]))

        # 清理数据以确保JSON序列化成功
        cleaned_result = clean_data_for_json_serialization(result)

        return ApiResponse(success=True, data=cleaned_result)

    except ValueError as e:
        logger.error("Invalid datetime format", error=str(e))
        raise HTTPException(
            status_code=400,
            detail="时间格式错误，请使用ISO格式，例如: 2024-01-15T10:00:00Z"
        )
    except Exception as e:
        logger.error("History search failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="搜索历史记录失败"
        )

@router.get("/sessions/{session_id}", response_model=ApiResponse[List[SessionDetail]])
async def get_session_details(session_id: str):
    """获取指定会话的详细信息"""
    try:
        session_data = await history_service.get_session_details(session_id)

        logger.info("Session details retrieved",
                   session_id=session_id,
                   record_count=len(session_data))

        return ApiResponse(success=True, data=session_data)

    except ValueError as e:
        logger.warning("Session not found", session_id=session_id)
        raise HTTPException(
            status_code=404,
            detail=f"会话 {session_id} 未找到"
        )
    except Exception as e:
        logger.error("Get session details failed",
                    session_id=session_id,
                    error=str(e))
        raise HTTPException(
            status_code=500,
            detail="获取会话详情失败"
        )

@router.get("/models", response_model=ApiResponse[List[str]])
async def get_models():
    """获取可用的模型ID列表"""
    try:
        models = await history_service.get_model_ids()

        logger.info("Models retrieved",
                   model_count=len(models),
                   models=models)

        return ApiResponse(success=True, data=models)

    except Exception as e:
        logger.error("Get models failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="获取模型列表失败"
        )

@router.get("/health", response_model=ApiResponse[HealthCheck])
async def health_check():
    """检查历史记录服务健康状态"""
    try:
        is_healthy = await history_service.test_connection()

        health_data = HealthCheck(
            status="healthy" if is_healthy else "unhealthy",
            service="HistoryService",
            timestamp=datetime.now()
        )

        logger.info("Health check completed", is_healthy=is_healthy)

        return ApiResponse(
            success=is_healthy,
            data=health_data
        )

    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return ApiResponse(
            success=False,
            data=HealthCheck(
                status="unhealthy",
                service="HistoryService",
                timestamp=datetime.now()
            )
        )