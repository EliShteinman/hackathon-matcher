from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.models.enums import MatchRequestStatus


class CreateMatchRequest(BaseModel):
    target_user_id: int = Field(..., description="ID of the user to request as partner")


class MatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    initiator_id: int
    target_id: int
    status: MatchRequestStatus
    created_at: datetime | None = None
    resolved_at: datetime | None = None


class TokenDetailsResponse(BaseModel):
    initiator_name: str
    initiator_branch: str
    target_name: str
    match_id: int
    is_expired: bool
    is_used: bool


class TokenActionResponse(BaseModel):
    message: str
    status: MatchRequestStatus
