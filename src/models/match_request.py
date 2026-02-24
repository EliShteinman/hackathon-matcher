from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.models.enums import MatchRequestStatus


class MatchRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = Field(default=None)
    initiator_id: int = Field(..., description="User ID of the match initiator")
    target_id: int = Field(..., description="User ID of the requested partner")
    status: MatchRequestStatus = Field(default=MatchRequestStatus.PENDING)
    created_at: datetime | None = Field(default=None)
    resolved_at: datetime | None = Field(default=None)
