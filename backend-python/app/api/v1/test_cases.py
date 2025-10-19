"""测试用例API路由"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from app.services.test_case_service import TestCaseService
from app.models.test_case import (
    TestCase, TestCaseCreate, TestCaseUpdate, BatchOperation
)
from app.models.common import ApiResponse
from app.utils.logger import logger

router = APIRouter()
test_case_service = TestCaseService()

@router.get("/", response_model=ApiResponse[dict])
async def get_test_cases(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    status: Optional[str] = Query(None, description="状态筛选"),
    domain: Optional[str] = Query(None, description="领域筛选"),
    priority: Optional[str] = Query(None, description="优先级筛选"),
    search: Optional[str] = Query(None, description="搜索关键词")
):
    """获取测试用例列表"""
    try:
        result = await test_case_service.get_test_cases(
            page=page,
            page_size=page_size,
            status=status,
            domain=domain,
            priority=priority,
            search=search
        )

        logger.info("Test cases retrieved",
                   page=page,
                   page_size=page_size,
                   status=status,
                   domain=domain,
                   priority=priority,
                   search=search,
                   results_count=len(result["items"]))

        return ApiResponse(success=True, data=result)

    except Exception as e:
        logger.error("Get test cases failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="获取测试用例列表失败"
        )

@router.get("/{test_case_id}", response_model=ApiResponse[dict])
async def get_test_case_by_id(test_case_id: str):
    """根据ID获取测试用例（完整结构）"""
    try:
        test_case = await test_case_service.get_test_case_by_id(test_case_id)

        if not test_case:
            logger.warning("Test case not found", test_case_id=test_case_id)
            raise HTTPException(
                status_code=404,
                detail=f"测试用例 {test_case_id} 未找到"
            )

        logger.info("Test case retrieved", test_case_id=test_case_id)
        return ApiResponse(success=True, data={"test_case": test_case})

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Get test case failed",
                    test_case_id=test_case_id,
                    error=str(e))
        raise HTTPException(
            status_code=500,
            detail="获取测试用例失败"
        )

@router.post("/", response_model=ApiResponse[TestCase])
async def create_test_case(request: TestCaseCreate):
    """创建测试用例"""
    try:
        test_case = await test_case_service.create_test_case(request)

        logger.info("Test case created",
                   test_case_id=test_case.id,
                   name=request.name)

        return ApiResponse(success=True, data=test_case)

    except Exception as e:
        logger.error("Create test case failed",
                    name=request.name,
                    error=str(e))
        raise HTTPException(
            status_code=500,
            detail="创建测试用例失败"
        )

@router.put("/{test_case_id}", response_model=ApiResponse[TestCase])
async def update_test_case(test_case_id: str, request: TestCaseUpdate):
    """更新测试用例"""
    try:
        test_case = await test_case_service.update_test_case(test_case_id, request)

        if not test_case:
            logger.warning("Test case not found for update", test_case_id=test_case_id)
            raise HTTPException(
                status_code=404,
                detail=f"测试用例 {test_case_id} 未找到"
            )

        logger.info("Test case updated", test_case_id=test_case_id)
        return ApiResponse(success=True, data=test_case)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Update test case failed",
                    test_case_id=test_case_id,
                    error=str(e))
        raise HTTPException(
            status_code=500,
            detail="更新测试用例失败"
        )

@router.delete("/{test_case_id}", response_model=ApiResponse[dict])
async def delete_test_case(test_case_id: str):
    """删除测试用例"""
    try:
        success = await test_case_service.delete_test_case(test_case_id)

        if not success:
            logger.warning("Test case not found for deletion", test_case_id=test_case_id)
            raise HTTPException(
                status_code=404,
                detail=f"测试用例 {test_case_id} 未找到"
            )

        logger.info("Test case deleted", test_case_id=test_case_id)
        return ApiResponse(success=True, data={"deleted": True})

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Delete test case failed",
                    test_case_id=test_case_id,
                    error=str(e))
        raise HTTPException(
            status_code=500,
            detail="删除测试用例失败"
        )

@router.post("/batch", response_model=ApiResponse[dict])
async def batch_operation(request: BatchOperation):
    """批量操作测试用例"""
    try:
        result = await test_case_service.batch_operation(request)

        logger.info("Batch operation completed",
                   action=request.action,
                   ids_count=len(request.ids),
                   affected_count=result["affected_count"])

        return ApiResponse(success=True, data=result)

    except Exception as e:
        logger.error("Batch operation failed",
                    action=request.action,
                    error=str(e))
        raise HTTPException(
            status_code=500,
            detail="批量操作失败"
        )

@router.get("/statistics/overview", response_model=ApiResponse[dict])
async def get_statistics():
    """获取测试用例统计信息"""
    try:
        stats = await test_case_service.get_statistics()

        logger.info("Statistics retrieved", total_count=stats["total_count"])
        return ApiResponse(success=True, data=stats)

    except Exception as e:
        logger.error("Get statistics failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="获取统计信息失败"
        )

@router.get("/tags", response_model=ApiResponse[list])
async def get_tags():
    """获取所有标签"""
    try:
        tags = await test_case_service.get_tags()

        logger.info("Tags retrieved", tag_count=len(tags))
        return ApiResponse(success=True, data=tags)

    except Exception as e:
        logger.error("Get tags failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="获取标签列表失败"
        )