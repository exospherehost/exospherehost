import pytest
from aiohttp import ClientSession

@pytest.mark.asyncio
async def test_health_endpoint(running_server):
    """Test using the session-scoped server (shared across tests)."""
    async with ClientSession() as session:
        async with session.get(f"{running_server.base_url}/health") as response:
            assert response.status == 200
            data = await response.json()
            assert data["message"] == "OK"