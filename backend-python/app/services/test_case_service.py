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

    def __init__(self):
        """初始化测试用例服务"""
        # 转换演示数据为DataFrame
        self.df = pd.DataFrame(MOCK_TEST_CASES)

        # 确保日期字段是datetime类型
        self.df['created_date'] = pd.to_datetime(self.df['created_date'], format='ISO8601')

        # 生成ID计数器
        self.id_counter = max(int(tc['id'].split('-')[1]) for tc in MOCK_TEST_CASES)

        logger.info("TestCaseService initialized", record_count=len(self.df))

    async def get_test_cases(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取测试用例列表"""
        logger.info("Getting test cases",
                   page=page,
                   page_size=page_size,
                   status=status,
                   search=search)

        filtered_df = self.df.copy()

        # 状态筛选
        if status:
            filtered_df = filtered_df[filtered_df['status'] == status]

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

        # 转换为字典格式
        items = []
        for _, row in page_data.iterrows():
            items.append({
                "id": row["id"],
                "name": row["name"],
                "description": row["description"],
                "status": row["status"],
                "owner": row["owner"],
                "priority": row["priority"],
                "domain": row["domain"],
                "difficulty": row["difficulty"],
                "created_date": row["created_date"].isoformat() + "Z",
                "updated_date": row.get("updated_date"),
                "tags": row["tags"]
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

    async def get_test_case_by_id(self, test_case_id: str) -> Optional[TestCase]:
        """根据ID获取测试用例"""
        logger.info("Getting test case by ID", test_case_id=test_case_id)

        test_case_data = self.df[self.df['id'] == test_case_id]

        if test_case_data.empty:
            logger.warning("Test case not found", test_case_id=test_case_id)
            return None

        row = test_case_data.iloc[0]
        test_case = TestCase(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            status=row["status"],
            owner=row["owner"],
            priority=row["priority"],
            domain=row["domain"],
            difficulty=row["difficulty"],
            created_date=row["created_date"],
            updated_date=row.get("updated_date"),
            tags=row["tags"]
        )

        logger.info("Test case retrieved", test_case_id=test_case_id)
        return test_case

    async def create_test_case(self, request: TestCaseCreate) -> TestCase:
        """创建测试用例"""
        self.id_counter += 1
        new_id = f"TC-{self.id_counter:04d}"

        new_test_case = TestCase(
            id=new_id,
            name=request.name,
            description=request.description,
            status=TestCaseStatus.DRAFT,
            owner=request.owner,
            priority=request.priority,
            domain=request.domain,
            difficulty=request.difficulty,
            created_date=datetime.now(),
            tags=request.tags
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

        stats = {
            "total_count": len(self.df),
            "status_distribution": self.df['status'].value_counts().to_dict(),
            "priority_distribution": self.df['priority'].value_counts().to_dict(),
            "difficulty_distribution": self.df['difficulty'].value_counts().to_dict(),
            "domain_distribution": self.df['domain'].value_counts().to_dict(),
        }

        logger.info("Statistics retrieved", total_count=stats["total_count"])
        return stats

    async def get_tags(self) -> List[str]:
        """获取所有标签"""
        logger.info("Getting all tags")

        all_tags = []
        for tags_list in self.df['tags']:
            if isinstance(tags_list, list):
                for tag in tags_list:
                    if isinstance(tag, dict) and 'name' in tag:
                        all_tags.append(tag['name'])

        unique_tags = sorted(list(set(all_tags)))

        logger.info("Tags retrieved", tag_count=len(unique_tags))
        return unique_tags