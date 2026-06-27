import pytest

from app.llm.factory import get_llm_provider


@pytest.mark.asyncio
async def test_generate():

    provider = get_llm_provider()

    response = await provider.generate(

        "Say hello in one sentence"

    )

    assert isinstance(response, str)

    assert len(response) > 0