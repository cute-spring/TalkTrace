from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union
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

    @field_validator('allowed_origins', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v

# 创建全局配置实例
settings = Settings()