from __future__ import annotations

import os
from functools import lru_cache

try:
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
                    try:
                        ids.add(int(raw))
                    except ValueError:
                        pass
            return ids

except ImportError:

    class Settings:  # type: ignore[no-redef]
        def __init__(self) -> None:
            self.bot_token = os.getenv("BOT_TOKEN", "")
            self.database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./kino.sqlite3")
            self.admin_ids = os.getenv("ADMIN_IDS", "")
            self.demo_mode = os.getenv("DEMO_MODE", "true").lower() in ("true", "1")
            self.log_level = os.getenv("LOG_LEVEL", "INFO")

        @property
        def admins(self) -> set[int]:
            ids: set[int] = set()
            for raw in self.admin_ids.split(","):
                raw = raw.strip()
                if raw:
                    try:
                        ids.add(int(raw))
                    except ValueError:
                        pass
            return ids


@lru_cache
def get_settings() -> Settings:
    return Settings()
