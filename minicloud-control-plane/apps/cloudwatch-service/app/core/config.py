from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./minicloud_cloudwatch.db"
    iam_auth_enabled: bool = False
    iam_base_url: str = "http://iam-service:8001"
    cloudwatch_service_token: str | None = None
    service_name: str = "cloudwatch-service"
    port: int = 8002

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

