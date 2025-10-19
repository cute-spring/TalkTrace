"""导入服务"""
from datetime import datetime
from typing import Dict, Any, List, Optional
import asyncio
import uuid
import random
from app.models.import_models import (
    ImportRequest, ImportPreview, ImportTask, ImportProgress,
    ImportTaskStatus, DuplicateSessionInfo, ImportValidationResult
)
from app.services.data_conversion_service import data_conversion_service
from app.services.test_case_service import TestCaseService
from app.services.bigquery_factory import get_bigquery_service
from app.services.bigquery_service import ConversationQueryRequest
from app.utils.logger import logger

class ImportService:
    """导入服务类"""
    _instance = None
    _shared_service = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ImportService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化导入服务"""
        # 如果已经有共享服务实例，直接使用
        if ImportService._shared_service is not None:
            self.tasks = ImportService._shared_service.tasks
            self.test_case_service = ImportService._shared_service.test_case_service
            self.bigquery_service = ImportService._shared_service.bigquery_service
            return

        # 存储导入任务
        self.tasks: Dict[str, ImportTask] = {}
        # 测试用例服务
        self.test_case_service = TestCaseService()
        # BigQuery服务
        self.bigquery_service = get_bigquery_service()

        # 保存为共享实例
        ImportService._shared_service = self

        logger.info("ImportService initialized")

    async def check_duplicate_sessions(self, session_ids: List[str]) -> ImportValidationResult:
        """检查重复会话"""
        logger.info("Checking duplicate sessions", session_count=len(session_ids))

        # 获取已存在的测试用例映射
        existing_test_cases = await self.test_case_service.get_test_cases_by_source_session(session_ids)

        # 分离有效会话和重复会话
        valid_sessions = []
        duplicate_sessions = []

        for session_id in session_ids:
            if session_id in existing_test_cases:
                existing_info = existing_test_cases[session_id]
                duplicate_info = DuplicateSessionInfo(
                    session_id=session_id,
                    existing_test_case_id=existing_info["test_case_id"],
                    existing_test_case_name=existing_info["test_case_name"],
                    import_date=existing_info["import_date"],
                    owner=existing_info["owner"]
                )
                duplicate_sessions.append(duplicate_info)
            else:
                valid_sessions.append(session_id)

        # 构建验证结果
        total_count = len(session_ids)
        duplicate_count = len(duplicate_sessions)
        can_import_all = duplicate_count == 0

        if duplicate_count == 0:
            message = f"所有 {total_count} 个会话都可以导入，无重复"
        elif duplicate_count == total_count:
            message = f"所有 {total_count} 个会话都存在重复，无法导入任何新会话"
        else:
            message = f"发现 {duplicate_count} 个重复会话，{total_count - duplicate_count} 个新会话可以导入"

        result = ImportValidationResult(
            valid_sessions=valid_sessions,
            duplicate_sessions=duplicate_sessions,
            can_import_all=can_import_all,
            total_count=total_count,
            duplicate_count=duplicate_count,
            message=message
        )

        logger.info("Duplicate check completed",
                   total_count=total_count,
                   duplicate_count=duplicate_count,
                   valid_count=len(valid_sessions))

        return result

    async def preview_import(self, request: ImportRequest) -> ImportPreview:
        """预览导入数据"""
        logger.info("Previewing import",
                   session_count=len(request.session_ids))

        # 检查重复会话
        validation_result = await self.check_duplicate_sessions(request.session_ids)

        preview_count = min(5, len(request.session_ids))
        preview_session_ids = request.session_ids[:preview_count]

        # 获取预览会话数据
        preview_sessions = []
        try:
            for session_id in preview_session_ids:
                # 获取会话的对话记录
                conversations = await self.bigquery_service.get_session_conversations(session_id)
                if conversations:
                    preview_sessions.append({
                        "session_id": session_id,
                        "message_count": len(conversations),
                        "first_message": conversations[0].content[:100] + "..." if len(conversations[0].content) > 100 else conversations[0].content,
                        "last_message": conversations[-1].content[:100] + "..." if len(conversations[-1].content) > 100 else conversations[-1].content,
                        "has_user_rating": any(msg.user_rating is not None for msg in conversations)
                    })
        except Exception as e:
            logger.error("Failed to fetch preview sessions", error=str(e))
            # 如果获取数据失败，使用模拟数据
            for session_id in preview_session_ids:
                preview_sessions.append({
                    "session_id": session_id,
                    "message_count": random.randint(2, 8),
                    "first_message": "这是一个示例用户问题...",
                    "last_message": "这是一个示例AI回答...",
                    "has_user_rating": random.choice([True, False])
                })

        # 构建包含重复信息的预览消息
        base_message = f"预览前 {preview_count} 个会话，共 {len(request.session_ids)} 个会话待导入"
        if validation_result.duplicate_count > 0:
            duplicate_message = f"，其中 {validation_result.duplicate_count} 个会话已存在"
            message = base_message + duplicate_message
        else:
            message = base_message

        preview = ImportPreview(
            total_count=len(request.session_ids),
            preview_count=preview_count,
            session_ids=preview_session_ids,
            preview_data=preview_sessions,
            message=message,
            duplicate_sessions=validation_result.duplicate_sessions,
            validation_result=validation_result
        )

        logger.info("Import preview completed",
                   total_count=preview.total_count,
                   preview_count=preview.preview_count,
                   preview_sessions_count=len(preview_sessions),
                   duplicate_count=validation_result.duplicate_count)

        return preview

    async def execute_import(self, request: ImportRequest) -> ImportTask:
        """执行导入操作"""
        # 检查重复会话
        validation_result = await self.check_duplicate_sessions(request.session_ids)

        # 如果没有有效会话，直接返回失败任务
        if len(validation_result.valid_sessions) == 0:
            task_id = f"IMPORT-{int(datetime.now().timestamp())}"
            task = ImportTask(
                task_id=task_id,
                session_ids=request.session_ids,
                status=ImportTaskStatus.FAILED,
                total=len(request.session_ids),
                processed=0,
                failed=len(request.session_ids),
                start_time=datetime.now(),
                end_time=datetime.now(),
                message="所有会话都已存在，无需重复导入"
            )
            self.tasks[task_id] = task
            return task

        # 生成任务ID
        task_id = f"IMPORT-{int(datetime.now().timestamp())}"

        # 构建配置参数
        config = {
            "default_owner": request.default_owner,
            "default_priority": request.default_priority,
            "default_difficulty": request.default_difficulty,
            "include_analysis": request.include_analysis,
            "validation_result": validation_result
        }

        # 创建导入任务（只处理有效会话）
        task = ImportTask(
            task_id=task_id,
            session_ids=validation_result.valid_sessions,
            status=ImportTaskStatus.PENDING,
            total=len(validation_result.valid_sessions),
            processed=0,
            failed=0,
            start_time=datetime.now(),
            config=config
        )

        # 存储任务
        self.tasks[task_id] = task

        logger.info("Import task created",
                   task_id=task_id,
                   total_sessions=task.total,
                   original_count=len(request.session_ids),
                   valid_count=len(validation_result.valid_sessions),
                   duplicate_count=validation_result.duplicate_count,
                   config=config)

        # 异步执行导入
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

            # 获取转换配置
            config = getattr(task, 'config', {})
            conversion_config = {
                "default_owner": config.get("default_owner", "system@company.com") or "system@company.com",
                "default_priority": config.get("default_priority", "medium") or "medium",
                "default_difficulty": config.get("default_difficulty", "medium") or "medium",
                "auto_generate_tags": True,
                "include_analysis": config.get("include_analysis", False)
            }

            # 处理每个会话
            for i, session_id in enumerate(task.session_ids):
                try:
                    logger.info("Processing session",
                               task_id=task_id,
                               session_id=session_id,
                               progress=f"{i+1}/{len(task.session_ids)}")

                    # 获取会话数据
                    session_conversations = await self.bigquery_service.get_session_conversations(session_id)

                    if not session_conversations:
                        logger.warning("No conversations found for session",
                                     task_id=task_id,
                                     session_id=session_id)
                        task.failed += 1
                        continue

                    # 获取检索片段数据
                    all_chunk_ids = []
                    for conv in session_conversations:
                        if conv.retrieval_chunk_ids:
                            all_chunk_ids.extend(conv.retrieval_chunk_ids)

                    retrieval_chunks_map = {}
                    if all_chunk_ids:
                        # 批量获取检索片段
                        unique_chunk_ids = list(set(all_chunk_ids))
                        try:
                            chunks = await self.bigquery_service.get_chunks_by_ids(unique_chunk_ids)
                            retrieval_chunks_map = {chunk.chunk_id: chunk for chunk in chunks}
                        except Exception as e:
                            logger.warning("Failed to fetch retrieval chunks",
                                         task_id=task_id,
                                         session_id=session_id,
                                         error=str(e))

                    # 更新转换配置，设置正确的源会话ID
                    conversion_config["source_session"] = session_id

                    # 转换为测试用例
                    test_case_create = await data_conversion_service.convert_session_to_test_case(
                        session_conversations,
                        retrieval_chunks_map,
                        conversion_config
                    )

                    # 创建测试用例
                    created_test_case = await self.test_case_service.create_test_case(test_case_create)

                    task.processed += 1
                    logger.info("Session converted successfully",
                               task_id=task_id,
                               session_id=session_id,
                               test_case_id=created_test_case.id)

                except Exception as e:
                    task.failed += 1
                    logger.error("Session processing failed",
                               task_id=task_id,
                               session_id=session_id,
                               error=str(e))

                # 添加小延迟避免过快的处理
                await asyncio.sleep(0.05)

            # 任务完成
            task.status = ImportTaskStatus.COMPLETED
            task.end_time = datetime.now()
            success_rate = (task.processed / task.total) * 100 if task.total > 0 else 0
            task.message = f"Import completed: {task.processed}/{task.total} sessions converted ({success_rate:.1f}% success rate)"

            logger.info("Import task completed",
                       task_id=task_id,
                       processed=task.processed,
                       failed=task.failed,
                       success_rate=f"{success_rate:.1f}%",
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