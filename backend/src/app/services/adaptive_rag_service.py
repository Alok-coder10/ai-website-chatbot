import re

from app.llm.factory import get_llm_provider
from app.cache.prompt_cache import get_prompt_cache
from app.services.metrics_service import get_metrics_service
from app.core.logger import log_debug, log_info

# ---------------------------------------------------------------------------
# Route names
# ---------------------------------------------------------------------------
NO_RETRIEVAL = "no_retrieval"   # greetings/chit-chat/meta questions -> skip RAG entirely
SIMPLE = "simple"               # direct factual question -> single-shot retrieval
COMPLEX = "complex"             # multi-part / vague / comparison -> full pipeline

VALID_ROUTES = {NO_RETRIEVAL, SIMPLE, COMPLEX}

# Cheap heuristics that let us skip an LLM call entirely for the most common
# no-retrieval cases (greetings, thanks, small talk). Anything that doesn't
# match falls through to the LLM classifier.
_GREETING_RE = re.compile(
    r"^\s*(hi|hey|hello|yo|sup|good\s?(morning|afternoon|evening|night))\s*[!.?]*\s*$",
    re.IGNORECASE,
)
_SMALL_TALK_RE = re.compile(
    r"^\s*(thanks|thank you|thx|ty|ok|okay|cool|great|nice|got it|bye|goodbye|"
    r"see ya|how are you|what'?s up|who are you|what can you do)\s*[!.?]*\s*$",
    re.IGNORECASE,
)


class AdaptiveRAGService:
    """
    Adaptive RAG router.

    Not every message needs the full expand -> multi-query -> HyDE ->
    hybrid-search -> rerank -> self-RAG-retry pipeline. Running all of
    that for "hi" or "thanks" wastes several LLM calls and, worse, forces
    the strict "answer ONLY from retrieved documents" prompt onto queries
    that were never going to retrieve anything — which is why chit-chat
    messages currently get answered with "I could not find this
    information."

    This service classifies each incoming message into one of three
    routes so the caller (AssistantService) can pick the right amount of
    work:

    - no_retrieval: skip retrieval entirely, answer conversationally
      using conversation history/memory only.
    - simple: single embed + one hybrid search pass, skip query
      expansion, multi-query fan-out, HyDE, and the self-RAG retry loop.
    - complex: the existing full pipeline (multi-hop, comparisons,
      vague or multi-part questions benefit from query expansion and
      HyDE).
    """

    def __init__(self):
        self.provider = get_llm_provider()
        self.prompt_cache = get_prompt_cache()
        self.metrics = get_metrics_service()

    def _heuristic_route(self, query: str) -> str | None:
        stripped = query.strip()

        if not stripped:
            return NO_RETRIEVAL

        if _GREETING_RE.match(stripped) or _SMALL_TALK_RE.match(stripped):
            return NO_RETRIEVAL

        return None

    async def classify(self, query: str) -> str:
        heuristic = self._heuristic_route(query)
        if heuristic is not None:
            log_debug(event="adaptive_rag_route", route=heuristic, source="heuristic")
            return heuristic

        cache_key = f"adaptive_route|{query.strip().lower()}"
        cached = self.prompt_cache.get(cache_key)

        if cached is not None:
            log_debug(event="cache_hit", cache="adaptive_rag_route")
            return cached

        prompt = f"""
        Classify how much document retrieval this question needs.

        Return EXACTLY one word:
        - NO_RETRIEVAL: greetings, small talk, thanks, or questions about
          the assistant itself that need no external documents.
        - SIMPLE: a direct factual question with one clear answer.
        - COMPLEX: a multi-part question, a comparison, a vague question,
          or one that likely needs several passages to answer fully.

        Question:
        {query}

        Answer with exactly one word: NO_RETRIEVAL, SIMPLE, or COMPLEX.
        """

        try:
            result = (await self.provider.generate(prompt=prompt)).strip().upper()
        except Exception as exc:
            log_debug(event="adaptive_rag_classify_failed", error=str(exc))
            return COMPLEX

        route = result.lower()
        if route not in VALID_ROUTES:
            # Be tolerant of extra words the LLM might add.
            for candidate in VALID_ROUTES:
                if candidate.upper() in result:
                    route = candidate
                    break
            else:
                route = COMPLEX

        self.prompt_cache.set(cache_key, route)
        self.metrics.cache_access("adaptive_rag_route_cache", False)

        log_info(event="adaptive_rag_route", route=route, source="llm", query=query)

        return route


_adaptive_rag_service = None


def get_adaptive_rag_service():
    global _adaptive_rag_service

    if _adaptive_rag_service is None:
        _adaptive_rag_service = AdaptiveRAGService()

    return _adaptive_rag_service
