from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    PROJECT_NAME: str = "A股行情分析系统"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"

    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"

    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    BACKEND_DEBUG: bool = True

    SECRET_KEY: str
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    DATA_SOURCE: str = "eastmoney"

    # 同花顺 iFinD HTTP API 配置
    IFIND_ACCOUNT: str = ""
    IFIND_PASSWORD: str = ""
    IFIND_REFRESH_TOKEN: str = ""
    IFIND_API_URL: str = "https://quantapi.51ifind.com/api/v1"

    ENABLE_ALERTS: bool = True
    ALERT_CHECK_INTERVAL: int = 60

    @property
    def CORS_ORIGINS(self) -> List[str]:
        try:
            return json.loads(self.ALLOWED_ORIGINS)
        except:
            return self.ALLOWED_ORIGINS.split(",")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
