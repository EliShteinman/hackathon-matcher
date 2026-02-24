from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    model_config = ConfigDict(env_prefix="DATABASE__")

    path: str = Field(default="hackathon_matcher.db", description="Path to SQLite database file")
    busy_timeout_ms: int = Field(default=5000, description="SQLite busy timeout in milliseconds")
    wal_mode: bool = Field(default=True, description="Enable WAL journal mode")
