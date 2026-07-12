from app.llm.factory import get_llm_provider

class QueryRewriteService:

    def __init__(self):
        self.provider = get_llm_provider()

    async def rewrite(self, question: str):

        prompt = f"""
        Rewrite this search query so it is easier for a retrieval system.

        Keep the meaning identical.

        Return only the rewritten query.

        Question:
        {question}
        """

        result = await self.provider.generate(
            prompt=prompt
        )

        return result.strip()