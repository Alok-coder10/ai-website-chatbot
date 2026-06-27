from app.core.config import settings
from app.llm.providers.ollama_provider import (
    OllamaProvider
)

def get_llm_provider():

    provider = settings.LLM_PROVIDER

    if provider == "ollama":
        return OllamaProvider()

    raise ValueError(
        f"Unsupported provider: {provider}"
    )