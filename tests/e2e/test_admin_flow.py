import io

from httpx import AsyncClient
from openpyxl import Workbook


class TestAdminFlow:
    async def _admin_login(self, client: AsyncClient) -> dict:
        resp = await client.post("/api/auth/admin/login", json={"username": "admin", "password": "admin"})
        assert resp.status_code == 200
        return dict(resp.cookies)

    async def test_admin_login(self, seeded_client: AsyncClient):
        resp = await seeded_client.post("/api/auth/admin/login", json={"username": "admin", "password": "admin"})
        assert resp.status_code == 200

    async def test_admin_login_invalid(self, seeded_client: AsyncClient):
        resp = await seeded_client.post("/api/auth/admin/login", json={"username": "admin", "password": "wrong"})
        assert resp.status_code == 401

    async def test_get_metrics(self, seeded_client: AsyncClient):
        cookies = await self._admin_login(seeded_client)
        resp = await seeded_client.get("/api/admin/metrics", cookies=cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        assert data["available"] == 3

    async def test_get_settings(self, seeded_client: AsyncClient):
        cookies = await self._admin_login(seeded_client)
        resp = await seeded_client.get("/api/admin/settings", cookies=cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_globally_locked"] is False

    async def test_update_settings_lock(self, seeded_client: AsyncClient):
        cookies = await self._admin_login(seeded_client)
        resp = await seeded_client.put(
            "/api/admin/settings",
            json={"is_globally_locked": True},
            cookies=cookies,
        )
        assert resp.status_code == 200
        assert resp.json()["is_globally_locked"] is True

    async def test_locked_system_blocks_match(self, seeded_client: AsyncClient):
        admin_cookies = await self._admin_login(seeded_client)
        await seeded_client.put("/api/admin/settings", json={"is_globally_locked": True}, cookies=admin_cookies)

        alice_resp = await seeded_client.post(
            "/api/auth/login", json={"id_number": "111111111", "email": "alice@test.com"}
        )
        alice_cookies = dict(alice_resp.cookies)

        match_resp = await seeded_client.post("/api/matches", json={"target_user_id": 2}, cookies=alice_cookies)
        assert match_resp.status_code == 423

    async def test_get_users_list(self, seeded_client: AsyncClient):
        cookies = await self._admin_login(seeded_client)
        resp = await seeded_client.get("/api/admin/users", cookies=cookies)
        assert resp.status_code == 200
        assert len(resp.json()) == 3

    async def test_excel_upload(self, seeded_client: AsyncClient):
        cookies = await self._admin_login(seeded_client)

        wb = Workbook()
        ws = wb.active
        ws.append(["id_number", "email", "full_name", "branch", "phone"])
        ws.append(["666666666", "frank@test.com", "Frank New", "Eilat", "050-6666"])
        buf = io.BytesIO()
        wb.save(buf)

        resp = await seeded_client.post(
            "/api/admin/excel/upload",
            files={
                "file": (
                    "new.xlsx",
                    buf.getvalue(),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
            cookies=cookies,
        )
        assert resp.status_code == 200
        assert resp.json()["imported_count"] == 1

        metrics = await seeded_client.get("/api/admin/metrics", cookies=cookies)
        assert metrics.json()["total"] == 4
