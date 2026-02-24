from src.exceptions.base import HackathonMatcherError


class LockError(HackathonMatcherError):
    pass


class SystemLockedError(LockError):
    def __init__(self) -> None:
        super().__init__(
            message="המערכת נעולה כעת, לא ניתן לבצע פעולות",
            error_code="SYSTEM_LOCKED",
        )


class DeadlinePassedError(LockError):
    def __init__(self) -> None:
        super().__init__(
            message="עבר המועד האחרון להתאמה",
            error_code="DEADLINE_PASSED",
        )
