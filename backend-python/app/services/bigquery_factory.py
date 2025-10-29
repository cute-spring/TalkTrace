"""BigQuery服务工厂"""
from typing import Union
from app.config import settings
from app.services.bigquery_service import BigQueryService
from app.services.mock_bigquery_service import MockBigQueryService
from app.services.real_bigquery_service import RealBigQueryService
from app.utils.logger import logger

class BigQueryServiceFactory:
    """BigQuery服务工厂类"""

    _instance: Union[BigQueryService, None] = None

    @classmethod
    def get_service(cls) -> BigQueryService:
        """获取BigQuery服务实例（单例模式）"""
        if cls._instance is None:
            cls._instance = cls._create_service()
            logger.info(
                "BigQuery service created",
                service_type=type(cls._instance).__name__,
                use_mock=settings.bigquery_use_mock
            )
        return cls._instance

    @classmethod
    def _create_service(cls) -> BigQueryService:
        """根据配置创建相应的服务实例"""
        if settings.use_real_bigquery:
            logger.info(
                "Creating real BigQuery service",
                project_id=settings.gcp_project_id,
                dataset_id=settings.gcp_dataset_id,
                credentials_path=settings.google_application_credentials
            )

            return RealBigQueryService(
                project_id=settings.gcp_project_id,
                dataset_id=settings.gcp_dataset_id,
                credentials_path=settings.google_application_credentials
            )
        else:
            logger.info("Creating mock BigQuery service")
            return MockBigQueryService()

    @classmethod
    def reset_instance(cls):
        """重置服务实例（主要用于测试）"""
        cls._instance = None
        logger.info("BigQuery service instance reset")

# 便捷函数
def get_bigquery_service() -> BigQueryService:
    """获取BigQuery服务的便捷函数"""
    return BigQueryServiceFactory.get_service()