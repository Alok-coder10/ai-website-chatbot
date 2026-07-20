from app.core.config import settings
from app.llm.providers.ollama_provider import (
    OllamaProvider
)
from app.core.logger import log_info

def get_llm_provider():

    provider = settings.LLM_PROVIDER
    log_info(
        event = "provider_selected",
        provider = provider
    )

    if provider == "ollama":
        return OllamaProvider()

    raise ValueError(
        f"Unsupported provider: {provider}"
    )