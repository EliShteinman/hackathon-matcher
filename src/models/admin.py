from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SystemSettings(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(default=1, description="Singleton row")
    is_globally_locked: bool = Field(default=False)
    deadline: datetime | None = Field(default=None, description="Auto-lock after this datetime")
    last_excel_upload_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)
