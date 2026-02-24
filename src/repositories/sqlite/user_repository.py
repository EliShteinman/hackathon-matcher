import logging
from datetime import UTC, datetime

import aiosqlite

from src.models.enums import UserStatus
from src.models.user import User
from src.repositories.interfaces.user_repository import UserRepositoryInterface

logger = logging.getLogger(__name__)


class SQLiteUserRepository(UserRepositoryInterface):
    def __init__(self, db: aiosqlite.Connection) -> None:
        self._db = db

    def _row_to_user(self, row: aiosqlite.Row) -> User:
        return User(
            id=row["id"],
            id_number=row["id_number"],
            email=row["email"],
            full_name=row["full_name"],
            branch=row["branch"],
            phone=row["phone"],
            status=UserStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
        )

    async def get_by_id(self, user_id: int) -> User | None:
        cursor = await self._db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = await cursor.fetchone()
        return self._row_to_user(row) if row else None

    async def get_by_id_number_and_email(self, id_number: str, email: str) -> User | None:
        cursor = await self._db.execute(
            "SELECT * FROM users WHERE id_number = ? AND LOWER(email) = LOWER(?)",
            (id_number, email),
        )
        row = await cursor.fetchone()
        return self._row_to_user(row) if row else None

    async def get_available_excluding(self, exclude_user_id: int) -> list[User]:
        cursor = await self._db.execute(
            "SELECT * FROM users WHERE status = ? AND id != ? ORDER BY full_name",
            (UserStatus.AVAILABLE.value, exclude_user_id),
        )
        rows = await cursor.fetchall()
        return [self._row_to_user(row) for row in rows]

    async def update_status(self, user_id: int, new_status: UserStatus) -> None:
        now = datetime.now(UTC).isoformat()
        await self._db.execute(
            "UPDATE users SET status = ?, updated_at = ? WHERE id = ?",
            (new_status.value, now, user_id),
        )

    async def update_status_with_lock(self, user_id: int, expected_status: UserStatus, new_status: UserStatus) -> bool:
        now = datetime.now(UTC).isoformat()
        cursor = await self._db.execute(
            "UPDATE users SET status = ?, updated_at = ? WHERE id = ? AND status = ?",
            (new_status.value, now, user_id, expected_status.value),
        )
        return cursor.rowcount > 0

    async def bulk_upsert(self, users: list[User]) -> int:
        now = datetime.now(UTC).isoformat()
        count = 0
        for user in users:
            cursor = await self._db.execute(
                """
                INSERT INTO users (id_number, email, full_name, branch, phone, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 'available', ?, ?)
                ON CONFLICT(id_number) DO UPDATE SET
                    email = excluded.email,
                    full_name = excluded.full_name,
                    branch = excluded.branch,
                    phone = excluded.phone,
                    updated_at = ?
                """,
                (user.id_number, user.email, user.full_name, user.branch, user.phone, now, now, now),
            )
            count += cursor.rowcount
        await self._db.commit()
        logger.info("Bulk upserted %d users", count)
        return count

    async def count_by_status(self) -> dict[UserStatus, int]:
        cursor = await self._db.execute("SELECT status, COUNT(*) as cnt FROM users GROUP BY status")
        rows = await cursor.fetchall()
        result: dict[UserStatus, int] = dict.fromkeys(UserStatus, 0)
        for row in rows:
            result[UserStatus(row["status"])] = row["cnt"]
        return result

    async def get_all(self) -> list[User]:
        cursor = await self._db.execute("SELECT * FROM users ORDER BY full_name")
        rows = await cursor.fetchall()
        return [self._row_to_user(row) for row in rows]
