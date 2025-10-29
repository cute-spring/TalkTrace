from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from app.models.test_case import TestCase, TestCaseCreate


class BaseTestCaseService(ABC):
    @abstractmethod
    async def get_test_cases(self, page: int, page_size: int, status: str, domain: str, priority: str, search: str):
        pass

    @abstractmethod
    async def get_test_case_by_id(self, test_case_id: str):
        pass

    @abstractmethod
    async def create_test_case(self, test_case: TestCaseCreate) -> TestCase:
        pass