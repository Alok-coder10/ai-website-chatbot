import time

from app.llm.factory import get_llm_provider
from app.cache.prompt_cache import get_prompt_cache
from app.services.metrics_service import get_metrics_service
from app.core.logger import log_debug, log_info


class HyDEService:
    """
    HyDE — Hypothetical Document Embeddings.

    Instead of embedding the raw user query (which is often short and
    vocabulary-mismatched with the source documents), we ask the LLM to
    write a short *hypothetical answer/passage* to the query first, and
    embed THAT. Hypothetical passages tend to look much more like the
    real chunks stored in Chroma, which improves semantic recall for
    vague, short, or under-specified queries.

    Reference: "Precise Zero-Shot Dense Retrieval without Relevance
    Labels" (Gao et al., 2022).
    """

    MAX_HYDE_CHARS = 1200

    def __init__(self):
        self.provider = get_llm_provider()
        self.prompt_cache = get_prompt_cache()
        self.metrics = get_metrics_service()

    async def generate(self, query: str) -> str:
        """
        Generate a hypothetical passage that would plausibly answer
        `query`. Falls back to the raw query on any failure so callers
        never break the retrieval pipeline because of HyDE.
        """
        if not query or not query.strip():
            return query

        cache_key = f"hyde|{query.strip().lower()}"
        cached = self.prompt_cache.get(cache_key)

        if cached is not None:
            log_debug(event="cache_hit", cache="hyde")
            return cached

        prompt = f"""
        Write a short, factual passage (3-5 sentences) that directly
        answers the question below, as if it were an excerpt taken from
        a knowledge-base document. Do not mention that you are guessing.
        Do not add disclaimers, headings, or bullet points. Plain prose
        only.

        Question:
        {query}

        Hypothetical passage:
        """

        start = time.perf_counter()
        try:
            hypothetical = (await self.provider.generate(prompt=prompt)).strip()
        except Exception as exc:
            log_debug(event="hyde_failed", error=str(exc))
            return query
        elapsed = time.perf_counter() - start

        if not hypothetical:
            return query

        if len(hypothetical) > self.MAX_HYDE_CHARS:
            hypothetical = hypothetical[: self.MAX_HYDE_CHARS]

        self.prompt_cache.set(cache_key, hypothetical)
        self.metrics.add_retrieval_metrics("hyde_time", elapsed)

        log_info(
            event="hyde_generated",
            query=query,
            hypothetical_chars=len(hypothetical),
        )

        return hypothetical


_hyde_service = None


def get_hyde_service():
    global _hyde_service

    if _hyde_service is None:
        _hyde_service = HyDEService()

    return _hyde_service
