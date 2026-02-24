import logging
from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from src.exceptions.auth_exceptions import AdminAuthenticationError, InvalidCredentialsError, SessionExpiredError
from src.models.user import User
from src.repositories.interfaces.user_repository import UserRepositoryInterface

logger = logging.getLogger(__name__)

_ALGORITHM = "HS256"
_SESSION_DURATION_HOURS = 24


class AuthService:
    def __init__(self, user_repository: UserRepositoryInterface, secret_key: str) -> None:
        self._user_repo = user_repository
        self._secret_key = secret_key

    async def authenticate(self, id_number: str, email: str) -> User:
        user = await self._user_repo.get_by_id_number_and_email(id_number, email)
        if user is None:
            logger.warning("Failed login attempt: id_number=%s, email=%s", id_number, email)
            raise InvalidCredentialsError
        logger.info("User authenticated: %s (%s)", user.full_name, user.id_number)
        return user

    def create_session_token(self, user_id: int) -> str:
        payload = {
            "sub": str(user_id),
            "type": "user",
            "exp": datetime.now(UTC) + timedelta(hours=_SESSION_DURATION_HOURS),
        }
        return jwt.encode(payload, self._secret_key, algorithm=_ALGORITHM)

    def create_admin_token(self) -> str:
        payload = {
            "sub": "admin",
            "type": "admin",
            "exp": datetime.now(UTC) + timedelta(hours=_SESSION_DURATION_HOURS),
        }
        return jwt.encode(payload, self._secret_key, algorithm=_ALGORITHM)

    def verify_session_token(self, token: str) -> int:
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[_ALGORITHM])
        except JWTError as exc:
            raise SessionExpiredError from exc
        if payload.get("type") != "user":
            raise SessionExpiredError
        return int(payload["sub"])

    def verify_admin_token(self, token: str) -> bool:
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[_ALGORITHM])
        except JWTError as exc:
            raise SessionExpiredError from exc
        return payload.get("type") == "admin"

    @staticmethod
    def verify_admin_credentials(username: str, password: str, expected_username: str, expected_password: str) -> None:
        if username != expected_username or password != expected_password:
            raise AdminAuthenticationError
