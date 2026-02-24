from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings

from config.database_settings import DatabaseSettings
from config.email_settings import EmailSettings
from config.excel_settings import ExcelSettings
from config.logging_settings import LoggingSettings


class AppSettings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    app_name: str = Field(default="Hackathon Matcher")
    base_url: str = Field(default="http://localhost:8000")
    session_secret_key: str = Field(default="change-me-to-a-random-secret-key")
    token_expiry_hours: int = Field(default=72, description="Email token expiry in hours")

    admin_username: str = Field(default="admin")
    admin_password: str = Field(default="admin")

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    email: EmailSettings = Field(default_factory=EmailSettings)
    excel: ExcelSettings = Field(default_factory=ExcelSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
