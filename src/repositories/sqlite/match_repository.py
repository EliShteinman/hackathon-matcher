import logging
from datetime import UTC, datetime

import aiosqlite

from src.models.enums import MatchRequestStatus
from src.models.match_request import MatchRequest
from src.repositories.interfaces.match_repository import MatchRepositoryInterface

logger = logging.getLogger(__name__)


class SQLiteMatchRepository(MatchRepositoryInterface):
    def __init__(self, db: aiosqlite.Connection) -> None:
        self._db = db

    def _row_to_match(self, row: aiosqlite.Row) -> MatchRequest:
        return MatchRequest(
            id=row["id"],
            initiator_id=row["initiator_id"],
            target_id=row["target_id"],
            status=MatchRequestStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            resolved_at=datetime.fromisoformat(row["resolved_at"]) if row["resolved_at"] else None,
        )

    async def create(self, match_request: MatchRequest) -> MatchRequest:
        cursor = await self._db.execute(
            """
            INSERT INTO match_requests (initiator_id, target_id, status)
            VALUES (?, ?, ?)
            """,
            (match_request.initiator_id, match_request.target_id, match_request.status.value),
        )
        match_request.id = cursor.lastrowid
        logger.info(
            "Created match request %d: %d -> %d", match_request.id, match_request.initiator_id, match_request.target_id
        )
        return match_request

    async def get_by_id(self, match_id: int) -> MatchRequest | None:
        cursor = await self._db.execute("SELECT * FROM match_requests WHERE id = ?", (match_id,))
        row = await cursor.fetchone()
        return self._row_to_match(row) if row else None

    async def get_active_by_user_id(self, user_id: int) -> MatchRequest | None:
        cursor = await self._db.execute(
            """
            SELECT * FROM match_requests
            WHERE (initiator_id = ? OR target_id = ?)
            AND status IN (?, ?)
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (user_id, user_id, MatchRequestStatus.PENDING.value, MatchRequestStatus.APPROVED.value),
        )
        row = await cursor.fetchone()
        return self._row_to_match(row) if row else None

    async def update_status(self, match_id: int, status: MatchRequestStatus, resolved_at: str | None = None) -> None:
        if resolved_at is None and status != MatchRequestStatus.PENDING:
            resolved_at = datetime.now(UTC).isoformat()
        await self._db.execute(
            "UPDATE match_requests SET status = ?, resolved_at = ? WHERE id = ?",
            (status.value, resolved_at, match_id),
        )
        logger.info("Updated match %d to status %s", match_id, status.value)
