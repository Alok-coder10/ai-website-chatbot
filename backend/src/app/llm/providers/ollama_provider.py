import httpx
import json
from app.core.config import settings
from app.llm.base import LLMProvider


class OllamaProvider(LLMProvider):

    async def generate(
        self,
        prompt: str
    ) -> str:

        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }

        async with httpx.AsyncClient(
            timeout=settings.LLM_TIMEOUT
        ) as client:

            response = await client.post(

                f"{settings.OLLAMA_HOST}/api/generate",

                json=payload

            )

            response.raise_for_status()

            data = response.json()

            return data["response"]

    
    async def stream_generate(self, prompt: str):
        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": True
        }

        async with httpx.AsyncClient(
            timeout= settings.LLM_TIMEOUT
        ) as client:

            async with client.stream(
                "POST", f"{settings.OLLAMA_HOST}/api/generate", json = payload
            ) as response:
                async for line in response.aiter_lines():

                    if not line:
                        continue

                    data = json.loads(line)
                    token = data.get("response", "")

                    if token:
                        yield token

                    if data.get("done", False):
                        break