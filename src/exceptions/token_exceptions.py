from src.exceptions.base import HackathonMatcherError


class TokenError(HackathonMatcherError):
    pass


class TokenNotFoundError(TokenError):
    def __init__(self) -> None:
        super().__init__(
            message="הקישור לא נמצא או לא תקין",
            error_code="TOKEN_NOT_FOUND",
        )


class TokenExpiredError(TokenError):
    def __init__(self) -> None:
        super().__init__(
            message="פג תוקף הקישור",
            error_code="TOKEN_EXPIRED",
        )


class TokenAlreadyUsedError(TokenError):
    def __init__(self) -> None:
        super().__init__(
            message="הקישור כבר נוצל",
            error_code="TOKEN_ALREADY_USED",
        )
