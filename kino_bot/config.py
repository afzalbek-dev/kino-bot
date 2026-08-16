from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = Field(default="", alias="BOT_TOKEN")
    database_url: str = Field(default="sqlite+aiosqlite:///./kino.sqlite3", alias="DATABASE_URL")
    admin_ids: str = Field(default="", alias="ADMIN_IDS")
    demo_mode: bool = Field(default=True, alias="DEMO_MODE")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def admins(self) -> set[int]:
        ids: set[int] = set()
        for raw in self.admin_ids.split(","):
            raw = raw.strip()
            if raw:
                ids.add(int(raw))
        return ids


@lru_cache
def get_settings() -> Settings:
    return Settings()
