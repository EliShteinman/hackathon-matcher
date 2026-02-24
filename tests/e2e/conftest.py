import io
import os
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from openpyxl import Workbook


@pytest_asyncio.fixture
async def app():
    os.environ["ADMIN_USERNAME"] = "admin"
    os.environ["ADMIN_PASSWORD"] = "admin"
    os.environ["SESSION_SECRET_KEY"] = "test-secret"
    os.environ["DATABASE__PATH"] = ":memory:"

    from config.app_settings import AppSettings

    AppSettings.model_config["env_file"] = None

    from src.app.main import create_app

    application = create_app()
    application.state.settings.database.path = ":memory:"
    application.state.settings.admin_username = "admin"
    application.state.settings.admin_password = "admin"

    from src.app.dependencies import get_settings

    get_settings.cache_clear()

    from src.repositories.sqlite.database import DatabaseManager
    from src.repositories.sqlite.migrations import run_migrations

    db_manager = DatabaseManager(application.state.settings.database)
    db = await db_manager.connect()
    await run_migrations(db)
    application.state.db_manager = db_manager
    application.state.db = db

    yield application

    await db_manager.disconnect()
    get_settings.cache_clear()


@pytest_asyncio.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def seeded_client(client: AsyncClient) -> AsyncClient:
    wb = Workbook()
    ws = wb.active
    ws.append(["id_number", "email", "full_name", "branch", "phone"])
    ws.append(["111111111", "alice@test.com", "Alice Cohen", "Tel Aviv", "050-1111"])
    ws.append(["222222222", "bob@test.com", "Bob Levy", "Jerusalem", "050-2222"])
    ws.append(["333333333", "carol@test.com", "Carol Shapira", "Haifa", "050-3333"])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    login_resp = await client.post("/api/auth/admin/login", json={"username": "admin", "password": "admin"})
    assert login_resp.status_code == 200, f"Admin login failed: {login_resp.json()}"
    cookies = login_resp.cookies

    resp = await client.post(
        "/api/admin/excel/upload",
        files={
            "file": ("test.xlsx", buf.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        },
        cookies=cookies,
    )
    assert resp.status_code == 200
    return client
