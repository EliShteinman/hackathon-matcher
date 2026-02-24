import io
from unittest.mock import AsyncMock

import pytest
from openpyxl import Workbook

from config.excel_settings import ExcelSettings
from src.exceptions.excel_exceptions import InvalidExcelFormatError, MissingRequiredColumnError
from src.services.excel_service import ExcelService


def create_test_excel(rows: list[list], sheet_name: str | None = None) -> bytes:
    wb = Workbook()
    ws = wb.active
    if sheet_name:
        ws.title = sheet_name
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


@pytest.fixture
def mock_user_repo():
    repo = AsyncMock()
    repo.bulk_upsert.return_value = 3
    return repo


@pytest.fixture
def excel_settings():
    return ExcelSettings()


@pytest.fixture
def excel_service(mock_user_repo, excel_settings):
    return ExcelService(mock_user_repo, excel_settings)


class TestImportFromBytes:
    async def test_valid_import(self, excel_service, mock_user_repo):
        data = create_test_excel(
            [
                ["id_number", "email", "full_name", "branch", "phone"],
                ["111", "a@t.com", "Alice", "TLV", "050"],
                ["222", "b@t.com", "Bob", "JLM", "051"],
            ]
        )
        count = await excel_service.import_from_bytes(data)
        assert count == 2
        mock_user_repo.bulk_upsert.assert_called_once()

    async def test_missing_required_column(self, excel_service):
        data = create_test_excel(
            [
                ["id_number", "email", "full_name"],
                ["111", "a@t.com", "Alice"],
            ]
        )
        with pytest.raises(MissingRequiredColumnError):
            await excel_service.import_from_bytes(data)

    async def test_invalid_file(self, excel_service):
        with pytest.raises(InvalidExcelFormatError):
            await excel_service.import_from_bytes(b"not an excel file")

    async def test_skips_invalid_rows(self, excel_service, mock_user_repo):
        data = create_test_excel(
            [
                ["id_number", "email", "full_name", "branch", "phone"],
                ["111", "a@t.com", "Alice", "TLV", "050"],
                ["", "b@t.com", "Bob", "JLM", "051"],
                ["333", "c@t.com", "Carol", "Haifa", None],
            ]
        )
        count = await excel_service.import_from_bytes(data)
        assert count == 2

    async def test_empty_sheet_raises(self, excel_service):
        data = create_test_excel([])
        with pytest.raises(InvalidExcelFormatError):
            await excel_service.import_from_bytes(data)

    async def test_no_valid_rows_raises(self, excel_service):
        data = create_test_excel(
            [
                ["id_number", "email", "full_name", "branch", "phone"],
            ]
        )
        with pytest.raises(InvalidExcelFormatError):
            await excel_service.import_from_bytes(data)
