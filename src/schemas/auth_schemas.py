from pydantic import BaseModel, ConfigDict, Field

from src.models.enums import UserStatus


class LoginRequest(BaseModel):
    id_number: str = Field(..., min_length=1)
    email: str = Field(...)


class AdminLoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_token: str
    user_id: int
    full_name: str
    status: UserStatus
