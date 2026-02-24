from src.exceptions.base import HackathonMatcherError


class MatchError(HackathonMatcherError):
    pass


class UserNotAvailableError(MatchError):
    def __init__(self) -> None:
        super().__init__(
            message="המשתמש כבר לא זמין להתאמה",
            error_code="USER_NOT_AVAILABLE",
        )


class SelfMatchError(MatchError):
    def __init__(self) -> None:
        super().__init__(
            message="לא ניתן לבחור את עצמך כשותף",
            error_code="SELF_MATCH",
        )


class AlreadyInMatchError(MatchError):
    def __init__(self) -> None:
        super().__init__(
            message="כבר יש לך בקשת התאמה פעילה",
            error_code="ALREADY_IN_MATCH",
        )


class NotInitiatorError(MatchError):
    def __init__(self) -> None:
        super().__init__(
            message="רק מי שיזם את ההתאמה יכול לבטל אותה",
            error_code="NOT_INITIATOR",
        )


class MatchNotFoundError(MatchError):
    def __init__(self) -> None:
        super().__init__(
            message="בקשת ההתאמה לא נמצאה",
            error_code="MATCH_NOT_FOUND",
        )
