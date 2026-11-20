import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_stream_endpoint_returns_response():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        timeout=30.0,
    ) as client:
        response = await client.post(
            "/api/v1/chat/stream",
            json={"message": "Tell me about my projects"},
        )

    assert response.status_code == 200
    assert response.text.strip()


@pytest.mark.asyncio
async def test_stream_endpoint_rejects_empty_message():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        timeout=30.0,
    ) as client:
        response = await client.post(
            "/api/v1/chat/stream",
            json={"message": ""},
        )

    assert response.status_code in (400, 422)
