from app.llm.factory import get_llm_provider

class QueryExpansionService:

    def __init__(self):
        self.provider = get_llm_provider()

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

        expanded = await self.provider.generate(
            prompt=prompt
        )

        return expanded.strip()