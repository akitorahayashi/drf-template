import httpx
import pytest

pytestmark = pytest.mark.asyncio


async def test_health_check(page_url: str):
    """
    Test the health check endpoint.
    """
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(f"{page_url}health/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
