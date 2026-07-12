from app.llm.factory import get_llm_provider
from app.cache.query_cache import get_query_cache
from app.cache.prompt_cache import get_prompt_cache

class QueryExpansionService:

    def __init__(self):
        self.provider = get_llm_provider()
        self.query_cache = get_query_cache()
        self.prompt_cache = get_prompt_cache()

    async def expand(self, query: str) -> str:
        prompt = f"""
        Expand the following search query.
        Rules:
        - Preserve the meaning.
        - Add related keywords.
        - Add abbreviations if useful.
        - Return ONLY the expanded query.
        - Do not use quotation marks.
        - Do not use bullet points.
        - Return one single line.
        - No explanations.

        Query:
        {query}
        """

        qcached = self.query_cache.get(query)

        if qcached is not None:
            print("Query Expansion Cache HIT")
            return qcached
        
        print("Query Expansion Cache MISS")

        pcached = self.prompt_cache.get(prompt)

        if pcached is not None:
            print("Prompt Cache HIT")
            self.query_cache.set(query, pcached)

            return pcached
        
        print("Prompt Cache MISS")

        expanded = await self.provider.generate(
            prompt=prompt
        )

        expanded = expanded.strip()
        self.prompt_cache.set(prompt, expanded)
        self.query_cache.set(query, expanded)

        return expanded


_query_expansion = None

def get_query_expansion_service():
    global _query_expansion
    
    if _query_expansion is None:
        _query_expansion = QueryExpansionService()

    return _query_expansion