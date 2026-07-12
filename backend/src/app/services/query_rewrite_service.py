from app.llm.factory import get_llm_provider
from app.cache.prompt_cache import get_prompt_cache

class QueryRewriteService:

    def __init__(self):
        self.provider = get_llm_provider()
        self.prompt_cache = get_prompt_cache()

    async def rewrite(self, question: str):

        prompt = f"""
        Rewrite this search query so it is easier for a retrieval system.

        Keep the meaning identical.

        Return only the rewritten query.

        Question:
        {question}
        """

        cached = self.prompt_cache.get(prompt)

        if cached is not None:
            print("Rewrite Prompt Cache HIT")
            return cached
        
        print("Rewrite Prompt Cache MISS")

        result = await self.provider.generate(
            prompt=prompt
        )

        result = result.strip()

        self.prompt_cache.set(prompt, result)

        return result


_query_rewrite = None

def get_query_rewrite_service():
    global _query_rewrite

    if _query_rewrite is None:
        _query_rewrite = QueryRewriteService()

    return _query_rewrite