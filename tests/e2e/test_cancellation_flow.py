from httpx import AsyncClient


class TestCancellationFlow:
    async def _login(self, client: AsyncClient, id_number: str, email: str) -> dict:
        resp = await client.post("/api/auth/login", json={"id_number": id_number, "email": email})
        assert resp.status_code == 200
        return dict(resp.cookies)

    async def _get_token_uuid(self, client: AsyncClient, match_id: int) -> str:
        db = client._transport.app.state.db
        from src.repositories.sqlite.token_repository import SQLiteTokenRepository

        token_repo = SQLiteTokenRepository(db)
        token = await token_repo.get_by_match_request_id(match_id)
        return token.uuid

    async def test_initiator_can_cancel_pending(self, seeded_client: AsyncClient):
        alice_cookies = await self._login(seeded_client, "111111111", "alice@test.com")

        available = await seeded_client.get("/api/users/available", cookies=alice_cookies)
        bob_id = next(u["id"] for u in available.json() if "Bob" in u["full_name"])

        match_resp = await seeded_client.post("/api/matches", json={"target_user_id": bob_id}, cookies=alice_cookies)
        match_id = match_resp.json()["id"]

        cancel_resp = await seeded_client.delete(f"/api/matches/{match_id}", cookies=alice_cookies)
        assert cancel_resp.status_code == 200

        alice_me = await seeded_client.get("/api/users/me", cookies=alice_cookies)
        assert alice_me.json()["status"] == "available"

    async def test_initiator_can_cancel_matched(self, seeded_client: AsyncClient):
        alice_cookies = await self._login(seeded_client, "111111111", "alice@test.com")

        available = await seeded_client.get("/api/users/available", cookies=alice_cookies)
        bob_id = next(u["id"] for u in available.json() if "Bob" in u["full_name"])

        match_resp = await seeded_client.post("/api/matches", json={"target_user_id": bob_id}, cookies=alice_cookies)
        match_id = match_resp.json()["id"]

        token_uuid = await self._get_token_uuid(seeded_client, match_id)
        await seeded_client.post(f"/api/tokens/{token_uuid}/approve")

        cancel_resp = await seeded_client.delete(f"/api/matches/{match_id}", cookies=alice_cookies)
        assert cancel_resp.status_code == 200

        alice_me = await seeded_client.get("/api/users/me", cookies=alice_cookies)
        assert alice_me.json()["status"] == "available"

    async def test_non_initiator_cannot_cancel(self, seeded_client: AsyncClient):
        alice_cookies = await self._login(seeded_client, "111111111", "alice@test.com")
        bob_cookies = await self._login(seeded_client, "222222222", "bob@test.com")

        available = await seeded_client.get("/api/users/available", cookies=alice_cookies)
        bob_id = next(u["id"] for u in available.json() if "Bob" in u["full_name"])

        match_resp = await seeded_client.post("/api/matches", json={"target_user_id": bob_id}, cookies=alice_cookies)
        match_id = match_resp.json()["id"]

        cancel_resp = await seeded_client.delete(f"/api/matches/{match_id}", cookies=bob_cookies)
        assert cancel_resp.status_code == 403
