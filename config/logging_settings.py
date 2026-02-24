from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class LoggingSettings(BaseSettings):
    model_config = ConfigDict(env_prefix="LOGGING__")

    level: str = Field(default="INFO", description="Root log level")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format string",
    )
    file_path: str | None = Field(default=None, description="Log file path (None for stdout only)")
