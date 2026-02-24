from src.models.enums import UserStatus
from src.models.user import User
from src.repositories.sqlite.user_repository import SQLiteUserRepository


class TestSQLiteUserRepository:
    async def test_bulk_upsert_and_get_all(self, user_repo: SQLiteUserRepository, sample_users: list[User]):
        count = await user_repo.bulk_upsert(sample_users)
        assert count == 5
        all_users = await user_repo.get_all()
        assert len(all_users) == 5

    async def test_get_by_id(self, user_repo: SQLiteUserRepository, sample_users: list[User]):
        await user_repo.bulk_upsert(sample_users)
        user = await user_repo.get_by_id(1)
        assert user is not None
        assert user.id_number == "111111111"

    async def test_get_by_id_not_found(self, user_repo: SQLiteUserRepository):
        user = await user_repo.get_by_id(999)
        assert user is None

    async def test_get_by_id_number_and_email(self, user_repo: SQLiteUserRepository, sample_users: list[User]):
        await user_repo.bulk_upsert(sample_users)
        user = await user_repo.get_by_id_number_and_email("111111111", "alice@test.com")
        assert user is not None
        assert user.full_name == "Alice Cohen"

    async def test_get_by_id_number_and_email_case_insensitive(
        self, user_repo: SQLiteUserRepository, sample_users: list[User]
    ):
        await user_repo.bulk_upsert(sample_users)
        user = await user_repo.get_by_id_number_and_email("111111111", "ALICE@TEST.COM")
        assert user is not None

    async def test_get_available_excluding(self, user_repo: SQLiteUserRepository, sample_users: list[User]):
        await user_repo.bulk_upsert(sample_users)
        available = await user_repo.get_available_excluding(1)
        assert len(available) == 4
        assert all(u.id != 1 for u in available)

    async def test_update_status(self, user_repo: SQLiteUserRepository, sample_users: list[User]):
        await user_repo.bulk_upsert(sample_users)
        await user_repo.update_status(1, UserStatus.PENDING)
        user = await user_repo.get_by_id(1)
        assert user.status == UserStatus.PENDING

    async def test_update_status_with_lock_success(self, user_repo: SQLiteUserRepository, sample_users: list[User]):
        await user_repo.bulk_upsert(sample_users)
        result = await user_repo.update_status_with_lock(1, UserStatus.AVAILABLE, UserStatus.PENDING)
        assert result is True
        user = await user_repo.get_by_id(1)
        assert user.status == UserStatus.PENDING

    async def test_update_status_with_lock_failure(self, user_repo: SQLiteUserRepository, sample_users: list[User]):
        await user_repo.bulk_upsert(sample_users)
        await user_repo.update_status(1, UserStatus.PENDING)
        result = await user_repo.update_status_with_lock(1, UserStatus.AVAILABLE, UserStatus.MATCHED)
        assert result is False

    async def test_count_by_status(self, user_repo: SQLiteUserRepository, sample_users: list[User]):
        await user_repo.bulk_upsert(sample_users)
        await user_repo.update_status(1, UserStatus.PENDING)
        await user_repo.update_status(2, UserStatus.MATCHED)
        counts = await user_repo.count_by_status()
        assert counts[UserStatus.AVAILABLE] == 3
        assert counts[UserStatus.PENDING] == 1
        assert counts[UserStatus.MATCHED] == 1

    async def test_upsert_updates_existing(self, user_repo: SQLiteUserRepository, sample_users: list[User]):
        await user_repo.bulk_upsert(sample_users)
        updated = [
            User(id_number="111111111", email="newemail@test.com", full_name="Alice Updated", branch="Ramat Gan")
        ]
        await user_repo.bulk_upsert(updated)
        user = await user_repo.get_by_id(1)
        assert user.email == "newemail@test.com"
        assert user.full_name == "Alice Updated"
        all_users = await user_repo.get_all()
        assert len(all_users) == 5
