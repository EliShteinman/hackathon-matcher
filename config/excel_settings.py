from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class ExcelSettings(BaseSettings):
    model_config = ConfigDict(env_prefix="EXCEL__")

    sheet_name: str | None = Field(default=None, description="Sheet name (None for first sheet)")
    column_id_number: str = Field(default="id_number", description="Column name for ID number")
    column_email: str = Field(default="email", description="Column name for email")
    column_full_name: str = Field(default="full_name", description="Column name for full name")
    column_branch: str = Field(default="branch", description="Column name for branch")
    column_phone: str = Field(default="phone", description="Column name for phone")
    header_row: int = Field(default=1, description="Row number containing column headers")
