from pydantic import BaseModel, ConfigDict, Field

from src.models.enums import UserStatus


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    branch: str
    status: UserStatus


class UserDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    id_number: str
    email: str
    full_name: str
    branch: str
    class_name: str | None
    status: UserStatus


class AvailableUserItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    branch: str
    display: str = Field(default="", description="Formatted display: full_name - branch")


class UserMeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    branch: str
    email: str
    class_name: str | None
    status: UserStatus
    match_info: "MatchInfoResponse | None" = None


class MatchInfoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    match_id: int
    partner_name: str
    partner_branch: str
    partner_email: str | None = None
    partner_class_name: str | None = None
    is_initiator: bool
    status: str
