import asyncio
import httpx

async def main():
    async with httpx.AsyncClient(timeout=None) as client:

        async with client.stream(
            "POST",
            "http://127.0.0.1:8000/api/v1/chat/stream",
            json={
                "message": "Tell me about my projects"
            },
        ) as response:

            async for chunk in response.aiter_text():
                print(chunk, end="", flush=True)

asyncio.run(main())