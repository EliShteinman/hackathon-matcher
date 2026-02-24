from collections.abc import AsyncGenerator

import aiosqlite
import pytest
import pytest_asyncio

from src.models.user import User
from src.repositories.sqlite.match_repository import SQLiteMatchRepository
from src.repositories.sqlite.migrations import run_migrations
from src.repositories.sqlite.settings_repository import SQLiteSettingsRepository
from src.repositories.sqlite.token_repository import SQLiteTokenRepository
from src.repositories.sqlite.user_repository import SQLiteUserRepository


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[aiosqlite.Connection, None]:
    connection = await aiosqlite.connect(":memory:")
    connection.row_factory = aiosqlite.Row
    await connection.execute("PRAGMA foreign_keys = ON")
    await run_migrations(connection)
    yield connection
    await connection.close()


@pytest_asyncio.fixture
async def user_repo(db: aiosqlite.Connection) -> SQLiteUserRepository:
    return SQLiteUserRepository(db)


@pytest_asyncio.fixture
async def match_repo(db: aiosqlite.Connection) -> SQLiteMatchRepository:
    return SQLiteMatchRepository(db)


@pytest_asyncio.fixture
async def token_repo(db: aiosqlite.Connection) -> SQLiteTokenRepository:
    return SQLiteTokenRepository(db)


@pytest_asyncio.fixture
async def settings_repo(db: aiosqlite.Connection) -> SQLiteSettingsRepository:
    return SQLiteSettingsRepository(db)


@pytest.fixture
def sample_users() -> list[User]:
    return [
        User(
            id_number="111111111", email="alice@test.com", full_name="Alice Cohen", branch="Tel Aviv", class_name="A1"
        ),
        User(id_number="222222222", email="bob@test.com", full_name="Bob Levy", branch="Jerusalem", class_name="B2"),
        User(id_number="333333333", email="carol@test.com", full_name="Carol Shapira", branch="Haifa", class_name="A1"),
        User(id_number="444444444", email="dave@test.com", full_name="Dave Mizrahi", branch="Beer Sheva"),
        User(id_number="555555555", email="eve@test.com", full_name="Eve Goldberg", branch="Tel Aviv", class_name="C3"),
    ]


@pytest_asyncio.fixture
async def populated_db(
    db: aiosqlite.Connection, user_repo: SQLiteUserRepository, sample_users: list[User]
) -> aiosqlite.Connection:
    await user_repo.bulk_upsert(sample_users)
    return db
