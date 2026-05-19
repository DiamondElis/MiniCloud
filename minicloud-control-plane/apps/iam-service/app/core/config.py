from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./minicloud_iam.db"
    jwt_secret: str = "local-dev-only-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expires_seconds: int = 3600
    service_name: str = "iam-service"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

