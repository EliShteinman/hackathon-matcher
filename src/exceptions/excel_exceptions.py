from src.exceptions.base import HackathonMatcherError


class ExcelImportError(HackathonMatcherError):
    pass


class InvalidExcelFormatError(ExcelImportError):
    def __init__(self, detail: str = "") -> None:
        super().__init__(
            message=f"פורמט קובץ Excel לא תקין: {detail}" if detail else "פורמט קובץ Excel לא תקין",
            error_code="INVALID_EXCEL_FORMAT",
        )


class MissingRequiredColumnError(ExcelImportError):
    def __init__(self, column_name: str) -> None:
        super().__init__(
            message=f"עמודה חובה חסרה: {column_name}",
            error_code="MISSING_REQUIRED_COLUMN",
        )
