import logging
from datetime import UTC, datetime

from src.models.admin import SystemSettings
from src.repositories.interfaces.settings_repository import SettingsRepositoryInterface
from src.services.excel_service import ExcelService

logger = logging.getLogger(__name__)


class AdminService:
    def __init__(
        self,
        settings_repository: SettingsRepositoryInterface,
        excel_service: ExcelService,
    ) -> None:
        self._settings_repo = settings_repository
        self._excel_service = excel_service

    async def get_settings(self) -> SystemSettings:
        return await self._settings_repo.get()

    async def update_settings(
        self, is_globally_locked: bool | None = None, deadline: datetime | None = ...
    ) -> SystemSettings:
        current = await self._settings_repo.get()
        if is_globally_locked is not None:
            current.is_globally_locked = is_globally_locked
        if deadline is not ...:
            current.deadline = deadline
        return await self._settings_repo.update(current)

    async def upload_excel(self, file_content: bytes) -> int:
        count = await self._excel_service.import_from_bytes(file_content)
        settings = await self._settings_repo.get()
        settings.last_excel_upload_at = datetime.now(UTC)
        await self._settings_repo.update(settings)
        logger.info("Admin uploaded Excel: %d users imported", count)
        return count
