from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_secret: str = "development-only-secret"
    roll_ttl_seconds: int = 300

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()

