import logging
from functools import lru_cache

from fastapi import Cookie, Depends, Request

from config.app_settings import AppSettings
from src.email_templates.template_renderer import TemplateRenderer
from src.exceptions.auth_exceptions import SessionExpiredError
from src.repositories.interfaces.match_repository import MatchRepositoryInterface
from src.repositories.interfaces.settings_repository import SettingsRepositoryInterface
from src.repositories.interfaces.token_repository import TokenRepositoryInterface
from src.repositories.interfaces.user_repository import UserRepositoryInterface
from src.repositories.sqlite.match_repository import SQLiteMatchRepository
from src.repositories.sqlite.settings_repository import SQLiteSettingsRepository
from src.repositories.sqlite.token_repository import SQLiteTokenRepository
from src.repositories.sqlite.user_repository import SQLiteUserRepository
from src.services.admin_service import AdminService
from src.services.auth_service import AuthService
from src.services.cancellation_service import CancellationService
from src.services.email_service import EmailService
from src.services.excel_service import ExcelService
from src.services.lock_service import LockService
from src.services.match_service import MatchService
from src.services.token_service import TokenService
from src.services.user_service import UserService

logger = logging.getLogger(__name__)


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()


@lru_cache
def get_template_renderer() -> TemplateRenderer:
    return TemplateRenderer()


def get_db(request: Request):
    return request.app.state.db


def get_user_repository(db=Depends(get_db)) -> UserRepositoryInterface:
    return SQLiteUserRepository(db)


def get_match_repository(db=Depends(get_db)) -> MatchRepositoryInterface:
    return SQLiteMatchRepository(db)


def get_token_repository(db=Depends(get_db)) -> TokenRepositoryInterface:
    return SQLiteTokenRepository(db)


def get_settings_repository(db=Depends(get_db)) -> SettingsRepositoryInterface:
    return SQLiteSettingsRepository(db)


def get_auth_service(
    user_repo: UserRepositoryInterface = Depends(get_user_repository),
    settings: AppSettings = Depends(get_settings),
) -> AuthService:
    return AuthService(user_repo, settings.session_secret_key)


def get_lock_service(
    settings_repo: SettingsRepositoryInterface = Depends(get_settings_repository),
) -> LockService:
    return LockService(settings_repo)


def get_email_service(
    settings: AppSettings = Depends(get_settings),
    renderer: TemplateRenderer = Depends(get_template_renderer),
) -> EmailService:
    return EmailService(settings.email, renderer)


def get_excel_service(
    user_repo: UserRepositoryInterface = Depends(get_user_repository),
    settings: AppSettings = Depends(get_settings),
) -> ExcelService:
    return ExcelService(user_repo, settings.excel)


def get_user_service(
    user_repo: UserRepositoryInterface = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repo)


def get_match_service(
    user_repo: UserRepositoryInterface = Depends(get_user_repository),
    match_repo: MatchRepositoryInterface = Depends(get_match_repository),
    token_repo: TokenRepositoryInterface = Depends(get_token_repository),
    lock_service: LockService = Depends(get_lock_service),
    email_service: EmailService = Depends(get_email_service),
    settings: AppSettings = Depends(get_settings),
) -> MatchService:
    return MatchService(
        user_repo,
        match_repo,
        token_repo,
        lock_service,
        email_service,
        token_expiry_hours=settings.token_expiry_hours,
        base_url=settings.base_url,
    )


def get_cancellation_service(
    user_repo: UserRepositoryInterface = Depends(get_user_repository),
    match_repo: MatchRepositoryInterface = Depends(get_match_repository),
    token_repo: TokenRepositoryInterface = Depends(get_token_repository),
    email_service: EmailService = Depends(get_email_service),
) -> CancellationService:
    return CancellationService(user_repo, match_repo, token_repo, email_service)


def get_token_service(
    token_repo: TokenRepositoryInterface = Depends(get_token_repository),
    match_repo: MatchRepositoryInterface = Depends(get_match_repository),
    match_service: MatchService = Depends(get_match_service),
) -> TokenService:
    return TokenService(token_repo, match_repo, match_service)


def get_admin_service(
    settings_repo: SettingsRepositoryInterface = Depends(get_settings_repository),
    excel_service: ExcelService = Depends(get_excel_service),
) -> AdminService:
    return AdminService(settings_repo, excel_service)


async def get_current_user_id(
    session_token: str | None = Cookie(default=None),
    auth_service: AuthService = Depends(get_auth_service),
) -> int:
    if not session_token:
        raise SessionExpiredError
    return auth_service.verify_session_token(session_token)


async def get_admin_verified(
    admin_token: str | None = Cookie(default=None),
    auth_service: AuthService = Depends(get_auth_service),
) -> bool:
    if not admin_token:
        raise SessionExpiredError
    return auth_service.verify_admin_token(admin_token)
