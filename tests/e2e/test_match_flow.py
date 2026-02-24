from httpx import AsyncClient


class TestMatchFlow:
    async def _login(self, client: AsyncClient, id_number: str, email: str) -> dict:
        resp = await client.post("/api/auth/login", json={"id_number": id_number, "email": email})
        assert resp.status_code == 200
        return dict(resp.cookies)

    async def test_full_match_approve_flow(self, seeded_client: AsyncClient):
        alice_cookies = await self._login(seeded_client, "111111111", "alice@test.com")

        available = await seeded_client.get("/api/users/available", cookies=alice_cookies)
        assert available.status_code == 200
        users = available.json()
        assert len(users) == 2
        bob_id = next(u["id"] for u in users if "Bob" in u["full_name"])

        match_resp = await seeded_client.post("/api/matches", json={"target_user_id": bob_id}, cookies=alice_cookies)
        assert match_resp.status_code == 200
        match_data = match_resp.json()
        assert match_data["status"] == "pending"

        alice_me = await seeded_client.get("/api/users/me", cookies=alice_cookies)
        assert alice_me.json()["status"] == "pending"

        from src.repositories.sqlite.token_repository import SQLiteTokenRepository

        db = seeded_client._transport.app.state.db
        token_repo = SQLiteTokenRepository(db)
        token = await token_repo.get_by_match_request_id(match_data["id"])
        assert token is not None

        approve_resp = await seeded_client.post(f"/api/tokens/{token.uuid}/approve")
        assert approve_resp.status_code == 200

        alice_me2 = await seeded_client.get("/api/users/me", cookies=alice_cookies)
        assert alice_me2.json()["status"] == "matched"

    async def test_full_match_reject_flow(self, seeded_client: AsyncClient):
        alice_cookies = await self._login(seeded_client, "111111111", "alice@test.com")

        available = await seeded_client.get("/api/users/available", cookies=alice_cookies)
        bob_id = next(u["id"] for u in available.json() if "Bob" in u["full_name"])

        match_resp = await seeded_client.post("/api/matches", json={"target_user_id": bob_id}, cookies=alice_cookies)
        match_data = match_resp.json()

        db = seeded_client._transport.app.state.db
        from src.repositories.sqlite.token_repository import SQLiteTokenRepository

        token_repo = SQLiteTokenRepository(db)
        token = await token_repo.get_by_match_request_id(match_data["id"])

        reject_resp = await seeded_client.post(f"/api/tokens/{token.uuid}/reject")
        assert reject_resp.status_code == 200

        alice_me = await seeded_client.get("/api/users/me", cookies=alice_cookies)
        assert alice_me.json()["status"] == "available"

    async def test_self_match_rejected(self, seeded_client: AsyncClient):
        alice_cookies = await self._login(seeded_client, "111111111", "alice@test.com")
        me = await seeded_client.get("/api/users/me", cookies=alice_cookies)
        alice_id = me.json()["id"]

        resp = await seeded_client.post("/api/matches", json={"target_user_id": alice_id}, cookies=alice_cookies)
        assert resp.status_code == 409
