import asyncio

from httpx import AsyncClient


class TestConcurrentMatching:
    async def _login(self, client: AsyncClient, id_number: str, email: str) -> dict:
        resp = await client.post("/api/auth/login", json={"id_number": id_number, "email": email})
        assert resp.status_code == 200
        return dict(resp.cookies)

    async def test_two_users_claim_same_target(self, seeded_client: AsyncClient):
        alice_cookies = await self._login(seeded_client, "111111111", "alice@test.com")
        carol_cookies = await self._login(seeded_client, "333333333", "carol@test.com")

        available = await seeded_client.get("/api/users/available", cookies=alice_cookies)
        bob_id = next(u["id"] for u in available.json() if "Bob" in u["full_name"])

        results = await asyncio.gather(
            seeded_client.post("/api/matches", json={"target_user_id": bob_id}, cookies=alice_cookies),
            seeded_client.post("/api/matches", json={"target_user_id": bob_id}, cookies=carol_cookies),
        )

        statuses = [r.status_code for r in results]
        assert 200 in statuses
        assert statuses.count(200) == 1
        failed_status = [s for s in statuses if s != 200][0]
        assert failed_status == 409
