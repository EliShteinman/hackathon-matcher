from fastapi import APIRouter, Depends, Response

from config.app_settings import AppSettings
from src.app.dependencies import get_auth_service, get_settings
from src.schemas.auth_schemas import AdminLoginRequest, LoginRequest, LoginResponse
from src.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(
    body: LoginRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.authenticate(body.id_number, body.email)
    token = auth_service.create_session_token(user.id)
    response.set_cookie(key="session_token", value=token, httponly=True, samesite="lax")
    return LoginResponse(
        session_token=token,
        user_id=user.id,
        full_name=user.full_name,
        status=user.status,
    )


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="session_token")
    return {"message": "התנתקת בהצלחה"}


@router.post("/admin/login")
async def admin_login(
    body: AdminLoginRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
    settings: AppSettings = Depends(get_settings),
):
    AuthService.verify_admin_credentials(body.username, body.password, settings.admin_username, settings.admin_password)
    token = auth_service.create_admin_token()
    response.set_cookie(key="admin_token", value=token, httponly=True, samesite="lax")
    return {"message": "התחברת בהצלחה כמנהל", "admin_token": token}
