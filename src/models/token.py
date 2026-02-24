from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EmailToken(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = Field(default=None)
    uuid: str = Field(..., description="Unique token string for email link")
    match_request_id: int = Field(..., description="FK to match_requests table")
    is_used: bool = Field(default=False)
    expires_at: datetime = Field(..., description="Token expiration datetime")
    created_at: datetime | None = Field(default=None)
