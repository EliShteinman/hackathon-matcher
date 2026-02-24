from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class ExcelSettings(BaseSettings):
    model_config = ConfigDict(env_prefix="EXCEL__", extra="ignore")

    sheet_name: str | None = Field(default=None, description="Sheet name (None for first sheet)")
    column_id_number: str = Field(default="מספר זהות", description="Column name for ID number")
    column_email: str = Field(default="email", description="Column name for email")
    column_full_name: str = Field(default="שם מלא", description="Column name for full name")
    column_branch: str = Field(default="סניף מכינה", description="Column name for branch")
    column_class_name: str = Field(default="כיתה", description="Column name for class")
    column_match_status: str = Field(default="סטטוס שידוך", description="Column name for match status (read-only)")
    header_row: int = Field(default=1, description="Row number containing column headers")
