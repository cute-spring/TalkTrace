"""导入服务"""
from datetime import datetime
from typing import Dict, Any, List, Optional
import asyncio
import uuid
from app.models.import_models import (
    ImportRequest, ImportPreview, ImportTask, ImportProgress,
    ImportTaskStatus
)
from app.utils.logger import logger

class ImportService:
    """导入服务类"""

    def __init__(self):
        """初始化导入服务"""
        # 存储导入任务
        self.tasks: Dict[str, ImportTask] = {}

        logger.info("ImportService initialized")

    async def preview_import(self, request: ImportRequest) -> ImportPreview:
        """预览导入数据"""
        logger.info("Previewing import",
                   session_count=len(request.session_ids))

        preview_count = min(5, len(request.session_ids))
        preview_session_ids = request.session_ids[:preview_count]

        preview = ImportPreview(
            total_count=len(request.session_ids),
            preview_count=preview_count,
            session_ids=preview_session_ids,
            message=f"预览前 {preview_count} 个会话"
        )

        logger.info("Import preview completed",
                   total_count=preview.total_count,
                   preview_count=preview.preview_count)

        return preview

    async def execute_import(self, request: ImportRequest) -> ImportTask:
        """执行导入操作"""
        # 生成任务ID
        task_id = f"IMPORT-{int(datetime.now().timestamp())}"

        # 创建导入任务
        task = ImportTask(
            task_id=task_id,
            session_ids=request.session_ids,
            status=ImportTaskStatus.PENDING,
            total=len(request.session_ids),
            processed=0,
            failed=0,
            start_time=datetime.now()
        )

        # 存储任务
        self.tasks[task_id] = task

        logger.info("Import task created",
                   task_id=task_id,
                   total_sessions=task.total)

        # 异步执行导入（模拟）
        asyncio.create_task(self._process_import_task(task_id))

        return task

    async def _process_import_task(self, task_id: str):
        """处理导入任务（后台执行）"""
        task = self.tasks.get(task_id)
        if not task:
            return

        try:
            # 更新任务状态为运行中
            task.status = ImportTaskStatus.RUNNING
            logger.info("Import task started", task_id=task_id)

            # 模拟导入过程
            for i, session_id in enumerate(task.session_ids):
                try:
                    # 模拟处理时间
                    await asyncio.sleep(0.1)

                    # 模拟成功率（90%成功）
                    import random
                    if random.random() > 0.1:
                        task.processed += 1
                    else:
                        task.failed += 1

                    logger.debug("Session processed",
                               task_id=task_id,
                               session_id=session_id,
                               processed=task.processed,
                               failed=task.failed)

                except Exception as e:
                    task.failed += 1
                    logger.error("Session processing failed",
                               task_id=task_id,
                               session_id=session_id,
                               error=str(e))

            # 任务完成
            task.status = ImportTaskStatus.COMPLETED
            task.end_time = datetime.now()
            task.message = "Import completed successfully"

            logger.info("Import task completed",
                       task_id=task_id,
                       processed=task.processed,
                       failed=task.failed,
                       duration=task.end_time - task.start_time)

        except Exception as e:
            # 任务失败
            task.status = ImportTaskStatus.FAILED
            task.end_time = datetime.now()
            task.message = f"Import failed: {str(e)}"

            logger.error("Import task failed",
                       task_id=task_id,
                       error=str(e))

    async def get_import_progress(self, task_id: str) -> Optional[ImportProgress]:
        """获取导入进度"""
        task = self.tasks.get(task_id)
        if not task:
            logger.warning("Import task not found", task_id=task_id)
            return None

        progress = ImportProgress(
            task_id=task.task_id,
            status=task.status,
            total=task.total,
            processed=task.processed,
            failed=task.failed,
            message=task.message,
            start_time=task.start_time,
            end_time=task.end_time
        )

        logger.debug("Import progress retrieved",
                    task_id=task_id,
                    progress=task.processed,
                    total=task.total)

        return progress

    async def get_import_tasks(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取导入任务列表"""
        logger.info("Getting import tasks",
                   page=page,
                   page_size=page_size)

        # 排序任务（按创建时间倒序）
        sorted_tasks = sorted(
            self.tasks.values(),
            key=lambda t: t.created_at,
            reverse=True
        )

        # 分页
        total = len(sorted_tasks)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_tasks = sorted_tasks[start_idx:end_idx]

        # 转换为字典格式
        items = []
        for task in page_tasks:
            items.append({
                "task_id": task.task_id,
                "session_ids": task.session_ids,
                "status": task.status,
                "total": task.total,
                "processed": task.processed,
                "failed": task.failed,
                "message": task.message,
                "start_time": task.start_time.isoformat() + "Z" if task.start_time else None,
                "end_time": task.end_time.isoformat() + "Z" if task.end_time else None,
                "created_at": task.created_at.isoformat() + "Z"
            })

        result = {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

        logger.info("Import tasks retrieved",
                   total_results=total,
                   page=page,
                   items_returned=len(items))

        return result

    async def delete_import_task(self, task_id: str) -> bool:
        """删除导入任务"""
        logger.info("Deleting import task", task_id=task_id)

        if task_id in self.tasks:
            del self.tasks[task_id]
            logger.info("Import task deleted", task_id=task_id)
            return True
        else:
            logger.warning("Import task not found for deletion", task_id=task_id)
            return False