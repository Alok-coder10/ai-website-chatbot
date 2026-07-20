import httpx
import json
import time
from app.core.config import settings
from app.llm.base import LLMProvider
from app.core.logger import (log_info, log_exception)

class OllamaProvider(LLMProvider):
    
    def __init__(self):
        self.provider_name = "ollama"
        self.model = settings.OLLAMA_MODEL

    async def generate(self, prompt: str) -> str:

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        
        async with httpx.AsyncClient(
            timeout=settings.LLM_TIMEOUT
        ) as client:

            log_info(
                event = "provider_request",
                provider = self.provider_name,
                model = self.model
            )
            try:
                start = time.perf_counter()
                response = await client.post(
                    f"{settings.OLLAMA_HOST}/api/generate", json=payload
                )
                elapsed = time.perf_counter() - start
                log_info(
                    event = "provider_response",
                    provider = self.provider_name,
                    latency_ms = round(elapsed * 1000, 2)
                )

                response.raise_for_status()

                data = response.json()

                return data["response"]
            except Exception as e:
                log_exception(
                    e, provider = self.provider_name
                )
                raise

    
    async def stream_generate(self, prompt: str):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True
        }

        log_info(
                event = "provider_request",
                provider = self.provider_name,
                model = self.model
        )

        async with httpx.AsyncClient(
            timeout= settings.LLM_TIMEOUT
        ) as client:

            try:
                start = time.perf_counter()

                async with client.stream(
                    "POST", f"{settings.OLLAMA_HOST}/api/generate", 
                    json = payload
                ) as response:
                    elapsed = time.perf_counter() - start
                    log_info(
                        event = "provider_response",
                        provider = self.provider_name,
                        latency_ms = round(elapsed * 1000, 2)
                    )
                    response.raise_for_status()

                    async for line in response.aiter_lines():

                        if not line:
                            continue

                        data = json.loads(line)
                        token = data.get("response", "")

                        if token:
                            yield token

                        if data.get("done", False):
                            break
            
            except Exception as e:
                log_exception(
                    e, provider = self.provider_name
                )
                raise

    
    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(
                timeout = 5
            ) as client:
                response = await client.get(
                    f"{settings.OLLAMA_HOST}/api/tags"
                )

                return response.status_code == 200
            
        except Exception:
            return False