class HackathonMatcherError(Exception):
    def __init__(self, message: str, error_code: str = "GENERAL_ERROR") -> None:
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
