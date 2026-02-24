from httpx import AsyncClient


class TestLoginFlow:
    async def test_login_success(self, seeded_client: AsyncClient):
        resp = await seeded_client.post("/api/auth/login", json={"id_number": "111111111", "email": "alice@test.com"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["full_name"] == "Alice Cohen"
        assert data["status"] == "available"
        assert "session_token" in resp.cookies

    async def test_login_invalid_credentials(self, seeded_client: AsyncClient):
        resp = await seeded_client.post("/api/auth/login", json={"id_number": "999999999", "email": "nobody@test.com"})
        assert resp.status_code == 401

    async def test_access_without_login(self, seeded_client: AsyncClient):
        resp = await seeded_client.get("/api/users/me")
        assert resp.status_code == 401

    async def test_logout(self, seeded_client: AsyncClient):
        login_resp = await seeded_client.post(
            "/api/auth/login", json={"id_number": "111111111", "email": "alice@test.com"}
        )
        cookies = login_resp.cookies

        logout_resp = await seeded_client.post("/api/auth/logout", cookies=cookies)
        assert logout_resp.status_code == 200

    async def test_get_me_after_login(self, seeded_client: AsyncClient):
        login_resp = await seeded_client.post(
            "/api/auth/login", json={"id_number": "111111111", "email": "alice@test.com"}
        )
        cookies = login_resp.cookies

        me_resp = await seeded_client.get("/api/users/me", cookies=cookies)
        assert me_resp.status_code == 200
        data = me_resp.json()
        assert data["full_name"] == "Alice Cohen"
        assert data["status"] == "available"
