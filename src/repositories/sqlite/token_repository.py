import logging
from datetime import datetime

import aiosqlite

from src.models.token import EmailToken
from src.repositories.interfaces.token_repository import TokenRepositoryInterface

logger = logging.getLogger(__name__)


class SQLiteTokenRepository(TokenRepositoryInterface):
    def __init__(self, db: aiosqlite.Connection) -> None:
        self._db = db

    def _row_to_token(self, row: aiosqlite.Row) -> EmailToken:
        return EmailToken(
            id=row["id"],
            uuid=row["uuid"],
            match_request_id=row["match_request_id"],
            is_used=bool(row["is_used"]),
            expires_at=datetime.fromisoformat(row["expires_at"]),
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
        )

    async def create(self, token: EmailToken) -> EmailToken:
        cursor = await self._db.execute(
            """
            INSERT INTO email_tokens (uuid, match_request_id, is_used, expires_at)
            VALUES (?, ?, ?, ?)
            """,
            (token.uuid, token.match_request_id, int(token.is_used), token.expires_at.isoformat()),
        )
        token.id = cursor.lastrowid
        logger.info("Created email token %s for match %d", token.uuid, token.match_request_id)
        return token

    async def get_by_uuid(self, uuid: str) -> EmailToken | None:
        cursor = await self._db.execute("SELECT * FROM email_tokens WHERE uuid = ?", (uuid,))
        row = await cursor.fetchone()
        return self._row_to_token(row) if row else None

    async def get_by_match_request_id(self, match_request_id: int) -> EmailToken | None:
        cursor = await self._db.execute(
            "SELECT * FROM email_tokens WHERE match_request_id = ? ORDER BY created_at DESC LIMIT 1",
            (match_request_id,),
        )
        row = await cursor.fetchone()
        return self._row_to_token(row) if row else None

    async def mark_used(self, token_id: int) -> None:
        await self._db.execute("UPDATE email_tokens SET is_used = 1 WHERE id = ?", (token_id,))
        logger.info("Marked token %d as used", token_id)
