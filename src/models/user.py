from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.models.enums import UserStatus


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    id: int | None = Field(default=None, description="Auto-incremented primary key")
    id_number: str = Field(..., min_length=1, description="Government-issued ID number")
    email: str = Field(..., description="User email address")
    full_name: str = Field(..., min_length=1, description="Full name")
    branch: str = Field(..., description="Branch or preparatory program")
    class_name: str | None = Field(default=None, description="Class name")
    status: UserStatus = Field(default=UserStatus.AVAILABLE)
    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)
