from app.llm.factory import get_llm_provider


def test_ollama_provider():
    provider = get_llm_provider()
    assert provider is not None
    