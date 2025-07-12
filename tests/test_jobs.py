import pytest
import asyncio
from uuid import uuid4
from httpx import AsyncClient, ASGITransport
from app.main import app


# Helper to register and log in a user, and return JWT headers
async def get_auth_headers(client: AsyncClient):
    username = f"user_{uuid4().hex[:8]}"
    password = "testpass"
    register_payload = {"username": username, "password": password}

    # Register user
    register_resp = await client.post("/register", json=register_payload)
    assert register_resp.status_code in (200, 201)

    # Login user 
    login_resp = await client.post("/login", json=register_payload)
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_job_submission_and_status():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await get_auth_headers(client)

        # Submit a job
        response = await client.post(
            "/jobs/",
            json={"data": [1, 2, 3], "operation": "square_sum"},
            headers=headers
        )
        assert response.status_code == 200
        job = response.json()
        job_id = job["job_id"]
        assert job["status"] == "PENDING"

        # Poll status until not pending
        for _ in range(30):
            status_resp = await client.get(f"/jobs/{job_id}/status", headers=headers)
            assert status_resp.status_code == 200
            status = status_resp.json()["status"]
            if status != "PENDING":
                break
            await asyncio.sleep(1)
        assert status in ("IN_PROGRESS", "SUCCESS", "FAILED")

        # Wait for job to complete
        for _ in range(30):
            status_resp = await client.get(f"/jobs/{job_id}/status", headers=headers)
            status = status_resp.json()["status"]
            if status in ("SUCCESS", "FAILED"):
                break
            await asyncio.sleep(1)
        assert status == "SUCCESS"

        # Retrieve result
        result_resp = await client.get(f"/jobs/{job_id}/result", headers=headers)
        assert result_resp.status_code == 200
        result = result_resp.json()["result"]
        assert result == 14  # 1^2 + 2^2 + 3^2 = 14

