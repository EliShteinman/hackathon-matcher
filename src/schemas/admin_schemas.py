from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.models.enums import UserStatus


class MetricsResponse(BaseModel):
    available: int = Field(default=0)
    pending: int = Field(default=0)
    matched: int = Field(default=0)
    total: int = Field(default=0)


class SystemSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    is_globally_locked: bool
    deadline: datetime | None
    last_excel_upload_at: datetime | None


class UpdateSettingsRequest(BaseModel):
    is_globally_locked: bool | None = None
    deadline: datetime | None = None


class ExcelUploadResponse(BaseModel):
    imported_count: int
    message: str


class AdminUserItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    id_number: str
    email: str
    full_name: str
    branch: str
    phone: str | None
    status: UserStatus
    partner_name: str | None = None
