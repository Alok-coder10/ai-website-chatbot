from app.llm.factory import get_llm_provider
from app.cache.query_cache import get_query_cache
from app.cache.prompt_cache import get_prompt_cache
from app.services.metrics_service import get_metrics_service
from app.core.logger import log_debug, log_info

class QueryService:

    def __init__(self):
        self.provider = get_llm_provider()
        self.query_cache = get_query_cache()
        self.prompt_cache = get_prompt_cache()
        self.metrics = get_metrics_service()

    
    async def generate_multi_queries(self, query: str) -> list[str]:
        prompt = f"""
        You are generating semantic retrieval queries for a RAG system.
        Rewrite the user's question into FIVE alternative search queries.

        Rules:
        - Keep the SAME intent.
        - Do NOT broaden the topic.
        - Do NOT introduce unrelated concepts.
        - Do NOT change the domain.
        - Each query should help retrieve different passages from the same document.
        - Return ONLY one query per line.
        - No numbering.
        - No explanations.

        User Question:
        {query}
        """
        cache_key = f"multi::{query}"
        cached = self.query_cache.get(cache_key)

        self.metrics.cache_access(
            "multi_query_cache",
            cached is not None
        )

        if cached is not None:
            log_debug(
                event = "cache_hit",
                cache = "multi_query_generation"
            )
            return cached
        
        log_debug(
            event = "cache_miss",
            cache = "multi_query_generation"
        )

        pcached = self.prompt_cache.get(prompt)

        self.metrics.cache_access(
            "prompt_cache",
            pcached is not None
        )
        if pcached is not None:
            log_debug(
                event="cache_hit",
                cache="prompt"
            )

            generated = [
                line.strip()
                for line in pcached.splitlines()
                if line.strip()
            ]
        else:
            log_debug(
                event= "cache_miss",
                cache = "prompt"
            )

            result = await self.provider.generate(prompt=prompt)

            log_info(
                event="multi_query_result:",
                result = repr(result)
            )

            if not result:
                return [query]
            
            result = result.strip()

            self.prompt_cache.set(
                prompt, result
            )

            generated = [
                line.strip()
                for line in result.splitlines()
                if line.strip()
            ]
        
        queries = [query]
        for q in generated:
            if q not in queries:
                queries.append(q)
        
        self.query_cache.set(
            cache_key, queries
        )
        
        return queries
        


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
        self.metrics.cache_access(
            "query_expansion_cache",
            qcached is not None
        )

        if qcached is not None:
            log_debug(
                event = "cache_hit",
                cache = "query_expansion"
            )
            return qcached
        
        log_debug(
                event = "cache_miss",
                cache = "query_expansion"
            )

        pcached = self.prompt_cache.get(prompt)

        self.metrics.cache_access(
            "prompt_cache",
            pcached is not None
        )

        if pcached is not None:
            log_debug(
                event = "cache_hit",
                cache = "prompt"
            )
            self.query_cache.set(query, pcached)

            return pcached
        
        log_debug(
                event = "cache_miss",
                cache = "prompt"
            )

        expanded = await self.provider.generate(
            prompt=prompt
        )

        expanded = expanded.strip()
        self.prompt_cache.set(prompt, expanded)
        self.query_cache.set(query, expanded)

        return expanded

    
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
            log_debug(
                event = "cache_hit",
                cache = "rewrite_prompt"
            )
            return cached
        
        log_debug(
                event = "cache_miss",
                cache = "rewrite_prompt"
            )

        result = await self.provider.generate(
            prompt=prompt
        )

        result = result.strip()

        self.prompt_cache.set(prompt, result)

        return result


_query_service = None

def get_query_service():
    global _query_service
    
    if _query_service is None:
        _query_service = QueryService()

    return _query_service