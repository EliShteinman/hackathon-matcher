import io

from openpyxl import Workbook

from config.excel_settings import ExcelSettings
from src.models.enums import UserStatus
from src.repositories.sqlite.user_repository import SQLiteUserRepository
from src.services.excel_service import ExcelService


def make_excel(rows: list[list]) -> bytes:
    wb = Workbook()
    ws = wb.active
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


class TestExcelImportFlow:
    async def test_full_import_pipeline(self, user_repo: SQLiteUserRepository, db):
        settings = ExcelSettings()
        service = ExcelService(user_repo, settings)

        data = make_excel(
            [
                ["מספר זהות", "email", "שם מלא", "סניף מכינה", "כיתה"],
                ["111111111", "alice@test.com", "Alice Cohen", "Tel Aviv", "A1"],
                ["222222222", "bob@test.com", "Bob Levy", "Jerusalem", "B2"],
                ["333333333", "carol@test.com", "Carol Shapira", "Haifa", None],
            ]
        )

        count = await service.import_from_bytes(data)
        assert count == 3

        all_users = await user_repo.get_all()
        assert len(all_users) == 3
        assert all(u.status == UserStatus.AVAILABLE for u in all_users)

    async def test_upsert_preserves_status(self, user_repo: SQLiteUserRepository, db):
        settings = ExcelSettings()
        service = ExcelService(user_repo, settings)

        data = make_excel(
            [
                ["מספר זהות", "email", "שם מלא", "סניף מכינה", "כיתה"],
                ["111111111", "alice@test.com", "Alice Cohen", "Tel Aviv", "A1"],
            ]
        )
        await service.import_from_bytes(data)

        await user_repo.update_status(1, UserStatus.MATCHED)

        data2 = make_excel(
            [
                ["מספר זהות", "email", "שם מלא", "סניף מכינה", "כיתה"],
                ["111111111", "alice_new@test.com", "Alice Cohen Updated", "Ramat Gan", "C3"],
            ]
        )
        await service.import_from_bytes(data2)

        user = await user_repo.get_by_id(1)
        assert user.email == "alice_new@test.com"
        assert user.full_name == "Alice Cohen Updated"
        assert user.status == UserStatus.MATCHED
