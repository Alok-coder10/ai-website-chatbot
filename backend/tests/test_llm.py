from app.llm.base import LLMProvider

def test_provider_exists():
    assert LLMProvider is not None