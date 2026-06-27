from app.core.config import settings

def get_llm_provider():

    provider = settings.LLM_PROVIDER

    if provider == "ollama":
        return None

    raise ValueError(
        f"Unsupported provider: {provider}"
    )