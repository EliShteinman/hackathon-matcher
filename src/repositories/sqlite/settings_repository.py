import logging
from datetime import UTC, datetime

import aiosqlite

from src.models.admin import SystemSettings
from src.repositories.interfaces.settings_repository import SettingsRepositoryInterface

logger = logging.getLogger(__name__)


class SQLiteSettingsRepository(SettingsRepositoryInterface):
    def __init__(self, db: aiosqlite.Connection) -> None:
        self._db = db

    def _row_to_settings(self, row: aiosqlite.Row) -> SystemSettings:
        return SystemSettings(
            id=row["id"],
            is_globally_locked=bool(row["is_globally_locked"]),
            deadline=datetime.fromisoformat(row["deadline"]) if row["deadline"] else None,
            last_excel_upload_at=(
                datetime.fromisoformat(row["last_excel_upload_at"]) if row["last_excel_upload_at"] else None
            ),
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
        )

    async def get(self) -> SystemSettings:
        cursor = await self._db.execute("SELECT * FROM system_settings WHERE id = 1")
        row = await cursor.fetchone()
        if row is None:
            return SystemSettings()
        return self._row_to_settings(row)

    async def update(self, settings: SystemSettings) -> SystemSettings:
        now = datetime.now(UTC).isoformat()
        await self._db.execute(
            """
            UPDATE system_settings SET
                is_globally_locked = ?,
                deadline = ?,
                last_excel_upload_at = ?,
                updated_at = ?
            WHERE id = 1
            """,
            (
                int(settings.is_globally_locked),
                settings.deadline.isoformat() if settings.deadline else None,
                settings.last_excel_upload_at.isoformat() if settings.last_excel_upload_at else None,
                now,
            ),
        )
        await self._db.commit()
        logger.info("Updated system settings: locked=%s, deadline=%s", settings.is_globally_locked, settings.deadline)
        return await self.get()
