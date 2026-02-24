from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from src.exceptions.lock_exceptions import DeadlinePassedError, SystemLockedError
from src.models.admin import SystemSettings
from src.services.lock_service import LockService


@pytest.fixture
def mock_settings_repo():
    return AsyncMock()


@pytest.fixture
def lock_service(mock_settings_repo):
    return LockService(mock_settings_repo)


class TestIsLocked:
    async def test_not_locked(self, lock_service, mock_settings_repo):
        mock_settings_repo.get.return_value = SystemSettings(is_globally_locked=False, deadline=None)
        assert await lock_service.is_locked() is False

    async def test_globally_locked(self, lock_service, mock_settings_repo):
        mock_settings_repo.get.return_value = SystemSettings(is_globally_locked=True, deadline=None)
        assert await lock_service.is_locked() is True

    async def test_deadline_passed(self, lock_service, mock_settings_repo):
        past = datetime.now(UTC) - timedelta(hours=1)
        mock_settings_repo.get.return_value = SystemSettings(is_globally_locked=False, deadline=past)
        assert await lock_service.is_locked() is True

    async def test_deadline_future(self, lock_service, mock_settings_repo):
        future = datetime.now(UTC) + timedelta(hours=24)
        mock_settings_repo.get.return_value = SystemSettings(is_globally_locked=False, deadline=future)
        assert await lock_service.is_locked() is False


class TestAssertNotLocked:
    async def test_raises_system_locked(self, lock_service, mock_settings_repo):
        mock_settings_repo.get.return_value = SystemSettings(is_globally_locked=True)
        with pytest.raises(SystemLockedError):
            await lock_service.assert_not_locked()

    async def test_raises_deadline_passed(self, lock_service, mock_settings_repo):
        past = datetime.now(UTC) - timedelta(hours=1)
        mock_settings_repo.get.return_value = SystemSettings(is_globally_locked=False, deadline=past)
        with pytest.raises(DeadlinePassedError):
            await lock_service.assert_not_locked()

    async def test_passes_when_not_locked(self, lock_service, mock_settings_repo):
        mock_settings_repo.get.return_value = SystemSettings(is_globally_locked=False, deadline=None)
        await lock_service.assert_not_locked()
