from src.exceptions.base import HackathonMatcherError


class AuthenticationError(HackathonMatcherError):
    pass


class InvalidCredentialsError(AuthenticationError):
    def __init__(self) -> None:
        super().__init__(
            message="מספר תעודת זהות או אימייל שגויים",
            error_code="INVALID_CREDENTIALS",
        )


class SessionExpiredError(AuthenticationError):
    def __init__(self) -> None:
        super().__init__(
            message="פג תוקף ההתחברות, יש להתחבר מחדש",
            error_code="SESSION_EXPIRED",
        )


class AdminAuthenticationError(AuthenticationError):
    def __init__(self) -> None:
        super().__init__(
            message="פרטי מנהל שגויים",
            error_code="ADMIN_AUTH_FAILED",
        )
