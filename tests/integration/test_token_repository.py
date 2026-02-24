from datetime import UTC, datetime, timedelta

from src.models.match_request import MatchRequest
from src.models.token import EmailToken
from src.repositories.sqlite.match_repository import SQLiteMatchRepository
from src.repositories.sqlite.token_repository import SQLiteTokenRepository


class TestSQLiteTokenRepository:
    async def test_create_and_get_by_uuid(
        self, token_repo: SQLiteTokenRepository, match_repo: SQLiteMatchRepository, populated_db
    ):
        mr = MatchRequest(initiator_id=1, target_id=2)
        mr = await match_repo.create(mr)
        await populated_db.commit()

        token = EmailToken(
            uuid="test-uuid-123",
            match_request_id=mr.id,
            expires_at=datetime.now(UTC) + timedelta(hours=72),
        )
        created = await token_repo.create(token)
        await populated_db.commit()

        assert created.id is not None
        fetched = await token_repo.get_by_uuid("test-uuid-123")
        assert fetched is not None
        assert fetched.match_request_id == mr.id
        assert fetched.is_used is False

    async def test_get_by_uuid_not_found(self, token_repo: SQLiteTokenRepository):
        result = await token_repo.get_by_uuid("nonexistent")
        assert result is None

    async def test_mark_used(self, token_repo: SQLiteTokenRepository, match_repo: SQLiteMatchRepository, populated_db):
        mr = MatchRequest(initiator_id=1, target_id=2)
        mr = await match_repo.create(mr)
        await populated_db.commit()

        token = EmailToken(
            uuid="test-uuid-mark",
            match_request_id=mr.id,
            expires_at=datetime.now(UTC) + timedelta(hours=72),
        )
        created = await token_repo.create(token)
        await populated_db.commit()

        await token_repo.mark_used(created.id)
        await populated_db.commit()

        fetched = await token_repo.get_by_uuid("test-uuid-mark")
        assert fetched.is_used is True

    async def test_get_by_match_request_id(
        self, token_repo: SQLiteTokenRepository, match_repo: SQLiteMatchRepository, populated_db
    ):
        mr = MatchRequest(initiator_id=1, target_id=2)
        mr = await match_repo.create(mr)
        await populated_db.commit()

        token = EmailToken(
            uuid="test-uuid-by-mr",
            match_request_id=mr.id,
            expires_at=datetime.now(UTC) + timedelta(hours=72),
        )
        await token_repo.create(token)
        await populated_db.commit()

        fetched = await token_repo.get_by_match_request_id(mr.id)
        assert fetched is not None
        assert fetched.uuid == "test-uuid-by-mr"
