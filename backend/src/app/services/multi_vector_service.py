import time

from app.llm.factory import get_llm_provider
from app.cache.prompt_cache import get_prompt_cache
from app.services.metrics_service import get_metrics_service
from app.core.logger import log_debug, log_info


class MultiVectorService:
    """
    Multi-vector retrieval: instead of storing exactly one embedding per
    chunk (the raw chunk text), we additionally embed a couple of other
    "views" of the same chunk:

    - summary: a one-sentence summary of the chunk, which often matches
      a user's short, high-level query better than the raw passage does.
    - questions: 2-3 hypothetical questions the chunk answers, which
      matches question-phrased queries directly (a user asking
      "how do I reset my password" is closer, embedding-wise, to the
      generated question "How do I reset my password?" than to a raw
      paragraph that never uses that phrasing).

    All views point back at the SAME chunk_id in Chroma's metadata, so
    at query time a match on ANY view resolves to the one real chunk
    stored in the SQL database — this only widens the net that catches
    a relevant chunk, it never creates duplicate content.

    This work happens once, at ingestion time, not per query — it adds
    latency to document upload, not to chat.
    """

    MIN_CONTENT_WORDS = 15  # skip tiny chunks, not worth extra views

    def __init__(self):
        self.provider = get_llm_provider()
        self.prompt_cache = get_prompt_cache()
        self.metrics = get_metrics_service()

    async def generate_views(self, content: str) -> dict:
        """
        Returns {"summary": str | None, "questions": str | None}.
        A None value means that view was skipped or failed to generate
        and should simply not be embedded/stored.
        """
        if not content or len(content.split()) < self.MIN_CONTENT_WORDS:
            return {"summary": None, "questions": None}

        summary = await self._generate(
            cache_prefix="mv_summary",
            content=content,
            instruction=(
                "Write ONE short sentence that summarizes the passage below. "
                "Return only the sentence, no preamble."
            ),
        )
        questions = await self._generate(
            cache_prefix="mv_questions",
            content=content,
            instruction=(
                "Write 3 short questions that the passage below directly "
                "answers. One question per line. No numbering, no "
                "preamble, no extra text."
            ),
        )

        return {"summary": summary, "questions": questions}

    async def _generate(self, cache_prefix: str, content: str, instruction: str):
        cache_key = f"{cache_prefix}|{hash(content)}"
        cached = self.prompt_cache.get(cache_key)

        if cached is not None:
            log_debug(event="cache_hit", cache=cache_prefix)
            return cached or None

        prompt = f"""
        {instruction}

        Passage:
        {content}
        """

        start = time.perf_counter()
        try:
            result = (await self.provider.generate(prompt=prompt)).strip()
        except Exception as exc:
            log_debug(event="multi_vector_generation_failed", cache=cache_prefix, error=str(exc))
            return None
        elapsed = time.perf_counter() - start

        self.metrics.add_retrieval_metrics("multi_vector_time", elapsed)
        self.prompt_cache.set(cache_key, result)

        if not result:
            return None

        return result


_multi_vector_service = None


def get_multi_vector_service():
    global _multi_vector_service

    if _multi_vector_service is None:
        _multi_vector_service = MultiVectorService()

    return _multi_vector_service
