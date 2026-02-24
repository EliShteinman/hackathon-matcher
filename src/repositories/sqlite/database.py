import logging

import aiosqlite

from config.database_settings import DatabaseSettings

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, settings: DatabaseSettings) -> None:
        self._settings = settings
        self._connection: aiosqlite.Connection | None = None

    async def connect(self) -> aiosqlite.Connection:
        self._connection = await aiosqlite.connect(self._settings.path)
        self._connection.row_factory = aiosqlite.Row

        await self._connection.execute(f"PRAGMA busy_timeout = {self._settings.busy_timeout_ms}")
        if self._settings.wal_mode:
            await self._connection.execute("PRAGMA journal_mode = WAL")
        await self._connection.execute("PRAGMA foreign_keys = ON")

        logger.info("Database connected: %s", self._settings.path)
        return self._connection

    async def disconnect(self) -> None:
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.info("Database disconnected")

    @property
    def connection(self) -> aiosqlite.Connection:
        if self._connection is None:
            msg = "Database not connected. Call connect() first."
            raise RuntimeError(msg)
        return self._connection
