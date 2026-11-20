from app.llm.factory import get_llm_provider
from app.cache.prompt_cache import get_prompt_cache
from app.core.logger import log_debug

class SelfRAGService:

    def __init__(self):
        self.provider = get_llm_provider()
        self.prompt_cache = get_prompt_cache()

    async def evaluate(self, question: str, context: str) -> str:

        prompt = f"""
        You are evaluating retrieved documents.
        Question:
        {question}

        Retrieved Context:
        {context}

        If the answer exists, copy the exact sentence from the context.
        If no sentence answers the question exactly, return:
        NONE

        Return ONLY the copied sentence or NONE.
        """

        cached = self.prompt_cache.get(prompt)

        if cached is not None:
            log_debug(
                event = "cache_hit",
                cache = "self_rag_prompt"
            )
            evidence = cached
        
        else:
            log_debug(
                event = "cache_miss",
                cache = "self_rag_prompt"
            )
            evidence = await self.provider.generate(
                prompt=prompt
            )
            evidence = evidence.strip()

            self.prompt_cache.set(prompt, evidence)

        
        if evidence == "NONE":
            return "NO"
        else:
            return "YES"



_selfrag = None

def get_self_rag_service():
    global _selfrag

    if _selfrag is None:
        _selfrag = SelfRAGService()

    return _selfrag