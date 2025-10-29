from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union, Optional
from pydantic import field_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_file_encoding="utf-8"
    )

    # Server Configuration
    port: int = 8001
    host: str = "0.0.0.0"
    environment: str = "development"

    # CORS Configuration
    allowed_origins: Union[str, List[str]] = ["http://localhost:3000", "http://localhost:5173"]

    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "json"

    # BigQuery Configuration
    bigquery_use_mock: bool = True  # 默认使用Mock服务
    gcp_project_id: Optional[str] = None
    gcp_dataset_id: Optional[str] = None
    gcp_table_id: str = "conversations"
    google_application_credentials: Optional[str] = None
    bigquery_use_real_test_cases: bool = False

    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    @field_validator('allowed_origins', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v

    @property
    def use_real_bigquery(self) -> bool:
        """是否使用真实BigQuery服务"""
        # 仅要求项目和数据集已配置即可尝试真实服务；
        # 表ID用于部分脚本，可选，不再作为切换条件。
        return (
            not self.bigquery_use_mock and
            self.gcp_project_id is not None and
            self.gcp_dataset_id is not None
        )

# 创建全局配置实例
settings = Settings()