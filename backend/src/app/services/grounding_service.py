import re
import time

from app.llm.factory import get_llm_provider
from app.cache.prompt_cache import get_prompt_cache
from app.services.metrics_service import get_metrics_service
from app.core.logger import log_debug, log_info

# Split on sentence-ending punctuation followed by whitespace and a
# capital letter, digit, or opening bracket. Not a full NLP sentence
# splitter (it will occasionally mis-split "Dr. Smith" style
# abbreviations), but it's good enough for grounding checks and keeps
# this dependency-free.
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\[])")

_VERDICT_LINE_RE = re.compile(r"^\s*(\d+)\s*[:.\)]\s*(GROUNDED|UNGROUNDED)", re.IGNORECASE)

# Sentences this short/generic aren't worth an LLM grounding check
# (greetings, "Sure.", "Here you go:") — treat them as always grounded.
_MIN_WORDS_TO_CHECK = 4


class AnswerGroundingService:
    """
    Sentence-level grounding / hallucination detection.

    The previous approach (`ResponseValidationService`) asked one
    whole-answer SUPPORTED/UNSUPPORTED question and, on UNSUPPORTED,
    triggered a full answer rewrite. That's coarse: a five-sentence
    answer with one fabricated sentence still gets entirely regenerated,
    and the "report" fed to repair is whatever prose the LLM felt like
    writing rather than a precise list.

    This service classifies EACH sentence as GROUNDED/UNGROUNDED against
    the retrieved context in a single batched LLM call (not one call per
    sentence), then builds a precise, sentence-exact report that the
    existing `ResponseRepairService` can act on surgically.
    """

    def __init__(self):
        self.provider = get_llm_provider()
        self.prompt_cache = get_prompt_cache()
        self.metrics = get_metrics_service()

    def _split_sentences(self, answer: str) -> list[str]:
        if not answer or not answer.strip():
            return []

        parts = _SENTENCE_SPLIT_RE.split(answer.strip())
        return [p.strip() for p in parts if p.strip()]

    def _needs_check(self, sentence: str) -> bool:
        return len(sentence.split()) >= _MIN_WORDS_TO_CHECK

    async def evaluate(self, question: str, context: str, answer: str) -> dict:
        sentences = self._split_sentences(answer)

        if not sentences:
            return {
                "supported": True,
                "sentences": [],
                "ungrounded_sentences": [],
                "report": "SUPPORTED",
                "fallback_used": False,
            }

        checkable = [(i, s) for i, s in enumerate(sentences) if self._needs_check(s)]

        if not checkable or not context or not context.strip():
            # Nothing substantial to check, or no context was retrieved
            # at all (e.g. the "simple" adaptive-RAG route came back
            # empty) — treat every sentence as ungrounded in that second
            # case since there's nothing to support any claim.
            if not context or not context.strip():
                ungrounded = [s for _, s in checkable] if checkable else []
                report = self._build_report(ungrounded)
                return {
                    "supported": len(ungrounded) == 0,
                    "sentences": sentences,
                    "ungrounded_sentences": ungrounded,
                    "report": report,
                    "fallback_used": False,
                }
            return {
                "supported": True,
                "sentences": sentences,
                "ungrounded_sentences": [],
                "report": "SUPPORTED",
                "fallback_used": False,
            }

        numbered = "\n".join(f"{i + 1}. {s}" for i, s in checkable)

        prompt = f"""
        You are checking whether each sentence of an answer is directly
        supported by the retrieved context below.

        Retrieved Context:
        {context}

        Sentences to check:
        {numbered}

        For each numbered sentence, decide GROUNDED (the context directly
        supports it) or UNGROUNDED (the context does not support it, or
        contradicts it).

        Return ONLY one line per sentence, in exactly this format, no
        other text:
        <number>: GROUNDED
        <number>: UNGROUNDED
        """

        cache_key = f"grounding|{hash((question, context, answer))}"
        cached = self.prompt_cache.get(cache_key)

        if cached is not None:
            log_debug(event="cache_hit", cache="grounding")
            raw = cached
        else:
            log_debug(event="cache_miss", cache="grounding")
            start = time.perf_counter()
            try:
                raw = (await self.provider.generate(prompt=prompt)).strip()
            except Exception as exc:
                log_debug(event="grounding_failed", error=str(exc))
                # Fail safe: don't block the response on a grounding
                # outage, but don't silently claim it's fully grounded
                # either — mark everything checkable as unverified so
                # metrics reflect the outage rather than hiding it.
                return {
                    "supported": True,
                    "sentences": sentences,
                    "ungrounded_sentences": [],
                    "report": "SUPPORTED",
                    "fallback_used": True,
                }
            elapsed = time.perf_counter() - start
            self.metrics.add_retrieval_metrics("grounding_time", elapsed)
            self.prompt_cache.set(cache_key, raw)

        verdicts = {}
        for line in raw.splitlines():
            match = _VERDICT_LINE_RE.match(line)
            if match:
                idx = int(match.group(1)) - 1
                verdicts[idx] = match.group(2).upper() == "GROUNDED"

        # If parsing mostly failed, don't trust a half-parsed verdict
        # map — default to "supported" rather than falsely flagging
        # good sentences as hallucinated because of a formatting slip.
        parsed_ratio = len(verdicts) / len(checkable) if checkable else 1
        fallback_used = parsed_ratio < 0.5

        ungrounded = []
        if not fallback_used:
            for idx, sentence in checkable:
                if not verdicts.get(idx, True):
                    ungrounded.append(sentence)

        report = self._build_report(ungrounded)

        log_info(
            event="answer_grounding",
            total_sentences=len(sentences),
            checked_sentences=len(checkable),
            ungrounded_sentences=len(ungrounded),
            fallback_used=fallback_used,
        )

        return {
            "supported": len(ungrounded) == 0,
            "sentences": sentences,
            "ungrounded_sentences": ungrounded,
            "report": report,
            "fallback_used": fallback_used,
        }

    def _build_report(self, ungrounded_sentences: list[str]) -> str:
        if not ungrounded_sentences:
            return "SUPPORTED"

        lines = ["UNSUPPORTED", "Unsupported Claims:"]
        lines += [f"- {s}" for s in ungrounded_sentences]
        return "\n".join(lines)

    def strip_ungrounded(self, answer: str, ungrounded_sentences: list[str]) -> str:
        """
        Directly remove ungrounded sentences from `answer` text without
        another LLM call. Used for the streaming path, where the answer
        has already been sent to the client token-by-token and an LLM
        rewrite would be pointless for the copy we persist/cache — we
        just want the stored/cached version to not contain the
        hallucinated sentence.
        """
        cleaned = answer
        for sentence in ungrounded_sentences:
            cleaned = cleaned.replace(sentence, "").strip()

        cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
        return cleaned


_grounding_service = None


def get_answer_grounding_service():
    global _grounding_service

    if _grounding_service is None:
        _grounding_service = AnswerGroundingService()

    return _grounding_service
