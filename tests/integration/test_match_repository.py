from src.models.enums import MatchRequestStatus
from src.models.match_request import MatchRequest
from src.repositories.sqlite.match_repository import SQLiteMatchRepository


class TestSQLiteMatchRepository:
    async def test_create_and_get(self, match_repo: SQLiteMatchRepository, populated_db):
        mr = MatchRequest(initiator_id=1, target_id=2)
        result = await match_repo.create(mr)
        await populated_db.commit()
        assert result.id is not None

        fetched = await match_repo.get_by_id(result.id)
        assert fetched is not None
        assert fetched.initiator_id == 1
        assert fetched.target_id == 2
        assert fetched.status == MatchRequestStatus.PENDING

    async def test_get_by_id_not_found(self, match_repo: SQLiteMatchRepository):
        result = await match_repo.get_by_id(999)
        assert result is None

    async def test_get_active_by_user_id_as_initiator(self, match_repo: SQLiteMatchRepository, populated_db):
        mr = MatchRequest(initiator_id=1, target_id=2)
        await match_repo.create(mr)
        await populated_db.commit()
        active = await match_repo.get_active_by_user_id(1)
        assert active is not None
        assert active.initiator_id == 1

    async def test_get_active_by_user_id_as_target(self, match_repo: SQLiteMatchRepository, populated_db):
        mr = MatchRequest(initiator_id=1, target_id=2)
        await match_repo.create(mr)
        await populated_db.commit()
        active = await match_repo.get_active_by_user_id(2)
        assert active is not None
        assert active.target_id == 2

    async def test_get_active_returns_none_for_cancelled(self, match_repo: SQLiteMatchRepository, populated_db):
        mr = MatchRequest(initiator_id=1, target_id=2)
        created = await match_repo.create(mr)
        await match_repo.update_status(created.id, MatchRequestStatus.CANCELLED)
        await populated_db.commit()
        active = await match_repo.get_active_by_user_id(1)
        assert active is None

    async def test_update_status(self, match_repo: SQLiteMatchRepository, populated_db):
        mr = MatchRequest(initiator_id=1, target_id=2)
        created = await match_repo.create(mr)
        await match_repo.update_status(created.id, MatchRequestStatus.APPROVED)
        await populated_db.commit()
        fetched = await match_repo.get_by_id(created.id)
        assert fetched.status == MatchRequestStatus.APPROVED
        assert fetched.resolved_at is not None
