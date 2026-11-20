from app.llm.providers.ollama_provider import OllamaProvider
from app.llm.providers.openai_provider import OpenAIProvider
from app.llm.providers.gemini_provider import GeminiProvider


if provider == "ollama":
    return OllamaProvider()

elif provider == "openai":
    return OpenAIProvider()

elif provider == "gemini":
    return GeminiProvider()

else:
    raise ValueError(f"Unsupported provider: {provider}")