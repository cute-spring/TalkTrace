"""导入API路由"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from app.services.import_service import ImportService
from app.models.import_models import (
    ImportRequest, ImportPreview, ImportTask, ImportProgress
)
from app.models.common import ApiResponse
from app.utils.logger import logger

router = APIRouter()

# 使用单例模式确保服务实例一致性
def get_import_service():
    """获取导入服务单例实例"""
    return ImportService()

# 获取共享的导入服务实例
import_service = get_import_service()

@router.post("/preview", response_model=ApiResponse[ImportPreview])
async def preview_import(request: ImportRequest):
    """预览导入数据"""
    try:
        preview = await import_service.preview_import(request)

        logger.info("Import preview completed",
                   session_count=len(request.session_ids),
                   preview_count=preview.preview_count)

        return ApiResponse(success=True, data=preview)

    except Exception as e:
        logger.error("Import preview failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="预览导入失败"
        )

@router.post("/execute", response_model=ApiResponse[ImportTask])
async def execute_import(request: ImportRequest):
    """执行导入操作"""
    try:
        task = await import_service.execute_import(request)

        logger.info("Import task started",
                   task_id=task.task_id,
                   total_sessions=task.total)

        return ApiResponse(success=True, data=task)

    except Exception as e:
        logger.error("Import execution failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="执行导入失败"
        )

@router.get("/progress/{task_id}", response_model=ApiResponse[ImportProgress])
async def get_import_progress(task_id: str):
    """获取导入进度"""
    try:
        progress = await import_service.get_import_progress(task_id)

        if not progress:
            logger.warning("Import task not found", task_id=task_id)
            raise HTTPException(
                status_code=404,
                detail=f"导入任务 {task_id} 未找到"
            )

        logger.debug("Import progress retrieved",
                    task_id=task_id,
                    progress=progress.processed,
                    total=progress.total)

        return ApiResponse(success=True, data=progress)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Get import progress failed",
                    task_id=task_id,
                    error=str(e))
        raise HTTPException(
            status_code=500,
            detail="获取导入进度失败"
        )

@router.get("/tasks", response_model=ApiResponse[dict])
async def get_import_tasks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小")
):
    """获取导入任务列表"""
    try:
        result = await import_service.get_import_tasks(
            page=page,
            page_size=page_size
        )

        logger.info("Import tasks retrieved",
                   page=page,
                   page_size=page_size,
                   results_count=len(result["items"]))

        return ApiResponse(success=True, data=result)

    except Exception as e:
        logger.error("Get import tasks failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="获取导入任务列表失败"
        )

@router.delete("/tasks/{task_id}", response_model=ApiResponse[dict])
async def delete_import_task(task_id: str):
    """删除导入任务"""
    try:
        success = await import_service.delete_import_task(task_id)

        if not success:
            logger.warning("Import task not found for deletion", task_id=task_id)
            raise HTTPException(
                status_code=404,
                detail=f"导入任务 {task_id} 未找到"
            )

        logger.info("Import task deleted", task_id=task_id)
        return ApiResponse(success=True, data={"deleted": True})

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Delete import task failed",
                    task_id=task_id,
                    error=str(e))
        raise HTTPException(
            status_code=500,
            detail="删除导入任务失败"
        )