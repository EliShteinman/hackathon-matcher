import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.exceptions.auth_exceptions import AuthenticationError
from src.exceptions.base import HackathonMatcherError
from src.exceptions.lock_exceptions import DeadlinePassedError, SystemLockedError
from src.exceptions.match_exceptions import (
    AlreadyInMatchError,
    MatchNotFoundError,
    NotInitiatorError,
    SelfMatchError,
    UserNotAvailableError,
)
from src.exceptions.token_exceptions import TokenAlreadyUsedError, TokenExpiredError, TokenNotFoundError

logger = logging.getLogger(__name__)

_STATUS_MAP: dict[type[HackathonMatcherError], int] = {
    AuthenticationError: 401,
    UserNotAvailableError: 409,
    AlreadyInMatchError: 409,
    SelfMatchError: 409,
    NotInitiatorError: 403,
    SystemLockedError: 423,
    DeadlinePassedError: 423,
    TokenNotFoundError: 404,
    MatchNotFoundError: 404,
    TokenExpiredError: 410,
    TokenAlreadyUsedError: 410,
}


def _get_status_code(exc: HackathonMatcherError) -> int:
    for exc_type, status_code in _STATUS_MAP.items():
        if isinstance(exc, exc_type):
            return status_code
    return 400


async def hackathon_exception_handler(_request: Request, exc: HackathonMatcherError) -> JSONResponse:
    status_code = _get_status_code(exc)
    logger.warning("Application error: %s (code=%s, status=%d)", exc.message, exc.error_code, status_code)
    return JSONResponse(
        status_code=status_code,
        content={"error_code": exc.error_code, "message": exc.message},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HackathonMatcherError, hackathon_exception_handler)
