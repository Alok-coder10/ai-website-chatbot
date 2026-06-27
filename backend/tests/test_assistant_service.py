import pytest
from app.services.assistant_service import (

    AssistantService
)

@pytest.mark.asyncio
async def test_chat():
    assistant = AssistantService()
    response = await assistant.chat(
        "Hello"
    )

    assert isinstance(
        response,
        str
    )

    assert len(
        response
    ) > 0