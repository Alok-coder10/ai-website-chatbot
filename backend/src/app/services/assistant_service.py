from app.llm.factory import get_llm_provider

class AssistantService:

    def __init__(self):
        self.provider = get_llm_provider()

    async def chat(self, message: str) -> str:
        response = await self.provider.generate(
            prompt=message
        )
        return response