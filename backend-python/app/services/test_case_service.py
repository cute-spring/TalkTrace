"""测试用例服务"""
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.test_case import (
    TestCase, TestCaseCreate, TestCaseUpdate, BatchOperation,
    TestCaseStatus, PriorityLevel, DifficultyLevel, Tag
)
from app.services.demo_data import MOCK_TEST_CASES
from app.utils.logger import logger

class TestCaseService:
    """测试用例服务类"""
    _instance = None
    _shared_service = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TestCaseService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化测试用例服务"""
        # 如果已经有共享服务实例，直接使用
        if TestCaseService._shared_service is not None:
            self.df = TestCaseService._shared_service.df
            self.id_counter = TestCaseService._shared_service.id_counter
            return

        # 转换演示数据为DataFrame
        self.df = pd.DataFrame(MOCK_TEST_CASES)

        # 确保日期字段是datetime类型
        self.df['created_date'] = pd.to_datetime(self.df['metadata'].apply(lambda x: x.get('created_date')), format='ISO8601')

        # 生成ID计数器
        self.id_counter = max(int(tc['id'].split('-')[1]) for tc in MOCK_TEST_CASES)

        # 保存为共享实例
        TestCaseService._shared_service = self

        logger.info("TestCaseService initialized", record_count=len(self.df))

    async def get_test_cases(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        domain: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取测试用例列表"""
        logger.info("Getting test cases",
                   page=page,
                   page_size=page_size,
                   status=status,
                   domain=domain,
                   priority=priority,
                   search=search)

        filtered_df = self.df.copy()

        # 状态筛选 - 兼容字典和对象两种格式
        if status:
            filtered_df = filtered_df[filtered_df['metadata'].apply(lambda x: (
                getattr(x, 'status', None) if hasattr(x, 'status') else x.get('status')
            )) == status]

        # 领域筛选
        if domain:
            filtered_df = filtered_df[filtered_df['domain'] == domain]

        # 优先级筛选 - 兼容字典和对象两种格式
        if priority:
            filtered_df = filtered_df[filtered_df['metadata'].apply(lambda x: (
                getattr(x, 'priority', None) if hasattr(x, 'priority') else x.get('priority')
            )) == priority]

        # 搜索
        if search:
            search_lower = search.lower()
            search_mask = (
                filtered_df['name'].str.lower().str.contains(search_lower, na=False) |
                filtered_df['description'].str.lower().str.contains(search_lower, na=False)
            )
            filtered_df = filtered_df[search_mask]

        # 排序
        filtered_df = filtered_df.sort_values('created_date', ascending=False)

        # 分页
        total = len(filtered_df)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_data = filtered_df.iloc[start_idx:end_idx]

        # 转换为简化的字典格式用于列表显示 - 兼容字典和对象两种格式
        items = []
        for _, row in page_data.iterrows():
            metadata = row["metadata"]

            # 辅助函数，兼容字典和对象两种格式
            def get_metadata_field(field_name):
                if hasattr(metadata, field_name):
                    return getattr(metadata, field_name, None)
                elif isinstance(metadata, dict):
                    return metadata.get(field_name)
                return None

            items.append({
                "id": row["id"],
                "name": row["name"],
                "description": row["description"],
                "status": get_metadata_field('status'),
                "owner": get_metadata_field('owner'),
                "priority": get_metadata_field('priority'),
                "domain": row["domain"],
                "difficulty": row["difficulty"],
                "created_date": get_metadata_field('created_date'),
                "updated_date": get_metadata_field('updated_date'),
                "tags": get_metadata_field('tags') or []
            })

        result = {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

        logger.info("Test cases retrieved",
                   total_results=total,
                   page=page,
                   items_returned=len(items))

        return result

    async def get_test_case_by_id(self, test_case_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取测试用例（完整结构）"""
        logger.info("Getting test case by ID", test_case_id=test_case_id)

        test_case_data = self.df[self.df['id'] == test_case_id]

        if test_case_data.empty:
            logger.warning("Test case not found", test_case_id=test_case_id)
            return None

        # 返回完整的测试用例数据
        test_case = test_case_data.iloc[0].to_dict()

        logger.info("Test case retrieved", test_case_id=test_case_id)
        return test_case

    async def create_test_case(self, request: TestCaseCreate) -> TestCase:
        """创建测试用例"""
        self.id_counter += 1
        new_id = f"TC-{self.id_counter:04d}"

        # 构建metadata结构
        from app.models.test_case import TestCaseMetadata
        metadata = TestCaseMetadata(
            status=TestCaseStatus.DRAFT,
            owner=request.owner,
            priority=request.priority,
            tags=request.tags,
            version="1.0",
            created_date=datetime.now().isoformat(),
            updated_date=datetime.now().isoformat(),
            source_session="import"
        )

        new_test_case = TestCase(
            id=new_id,
            name=request.name,
            description=request.description,
            metadata=metadata,
            domain=request.domain,
            difficulty=request.difficulty,
            test_config=request.test_config,
            input=request.input,
            execution=request.execution,
            analysis=request.analysis
        )

        # 添加到DataFrame
        new_row = new_test_case.model_dump()
        new_df = pd.DataFrame([new_row])
        self.df = pd.concat([self.df, new_df], ignore_index=True)

        logger.info("Test case created", test_case_id=new_id, name=request.name)
        return new_test_case

    async def update_test_case(self, test_case_id: str, request: TestCaseUpdate) -> Optional[TestCase]:
        """更新测试用例"""
        logger.info("Updating test case", test_case_id=test_case_id)

        # 查找测试用例
        idx = self.df[self.df['id'] == test_case_id].index
        if len(idx) == 0:
            logger.warning("Test case not found for update", test_case_id=test_case_id)
            return None

        # 更新字段
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            self.df.at[idx[0], field] = value

        # 更新修改时间
        self.df.at[idx[0], 'updated_date'] = datetime.now()

        # 返回更新后的测试用例
        return await self.get_test_case_by_id(test_case_id)

    async def delete_test_case(self, test_case_id: str) -> bool:
        """删除测试用例"""
        logger.info("Deleting test case", test_case_id=test_case_id)

        initial_count = len(self.df)
        self.df = self.df[self.df['id'] != test_case_id]
        deleted = len(self.df) < initial_count

        if deleted:
            logger.info("Test case deleted", test_case_id=test_case_id)
        else:
            logger.warning("Test case not found for deletion", test_case_id=test_case_id)

        return deleted

    async def batch_operation(self, request: BatchOperation) -> Dict[str, Any]:
        """批量操作测试用例"""
        logger.info("Performing batch operation",
                   action=request.action,
                   ids_count=len(request.ids))

        affected_count = 0

        if request.action == "delete":
            initial_count = len(self.df)
            self.df = self.df[~self.df['id'].isin(request.ids)]
            affected_count = initial_count - len(self.df)

        elif request.action == "update_status" and request.data:
            new_status = request.data.get("status")
            if new_status:
                mask = self.df['id'].isin(request.ids)
                self.df.loc[mask, 'status'] = new_status
                self.df.loc[mask, 'updated_date'] = datetime.now()
                affected_count = mask.sum()

        logger.info("Batch operation completed",
                   action=request.action,
                   affected_count=affected_count)

        return {
            "affected_count": affected_count,
            "action": request.action
        }

    async def get_statistics(self) -> Dict[str, Any]:
        """获取测试用例统计信息"""
        logger.info("Getting test case statistics")

        # 提取统计信息，兼容字典和对象两种格式
        def get_status_value(metadata):
            if hasattr(metadata, 'status'):
                return getattr(metadata, 'status', None)
            elif isinstance(metadata, dict):
                return metadata.get('status')
            return None

        def get_priority_value(metadata):
            if hasattr(metadata, 'priority'):
                return getattr(metadata, 'priority', None)
            elif isinstance(metadata, dict):
                return metadata.get('priority')
            return None

        status_list = self.df['metadata'].apply(get_status_value)
        priority_list = self.df['metadata'].apply(get_priority_value)

        stats = {
            "total_count": len(self.df),
            "status_distribution": status_list.value_counts().to_dict(),
            "priority_distribution": priority_list.value_counts().to_dict(),
            "difficulty_distribution": self.df['difficulty'].value_counts().to_dict(),
            "domain_distribution": self.df['domain'].value_counts().to_dict(),
        }

        logger.info("Statistics retrieved", total_count=stats["total_count"])
        return stats

    async def get_tags(self) -> List[str]:
        """获取所有标签"""
        logger.info("Getting all tags")

        all_tags = []
        for metadata in self.df['metadata']:
            # 兼容字典和对象两种格式获取tags
            if hasattr(metadata, 'tags'):
                tags = getattr(metadata, 'tags', [])
            elif isinstance(metadata, dict):
                tags = metadata.get('tags', [])
            else:
                tags = []

            if isinstance(tags, list):
                for tag in tags:
                    if hasattr(tag, 'name'):
                        all_tags.append(tag.name)
                    elif isinstance(tag, dict) and 'name' in tag:
                        all_tags.append(tag['name'])

        unique_tags = sorted(list(set(all_tags)))

        logger.info("Tags retrieved", tag_count=len(unique_tags))
        return unique_tags