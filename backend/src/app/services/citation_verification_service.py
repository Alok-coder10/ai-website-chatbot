import re

from app.core.logger import log_debug, log_info

# Matches the format the prompt asks the model to produce:
#   [Source: filename chunk N]
# Tolerant of minor variations: optional comma before "chunk", extra
# whitespace, "Source" without the colon.
_CITATION_RE = re.compile(
    r"\[\s*Source\s*:?\s*(?P<name>[^\],]+?)\s*,?\s*chunk\s*(?P<chunk>\d+)\s*\]",
    re.IGNORECASE,
)

# Matches the ground-truth citation strings produced by
# RetrievalService.build_parent_context(): "filename(chunk N)"
_KNOWN_RE = re.compile(
    r"^(?P<name>.+?)\(chunk\s*(?P<chunk>\d+)\)$",
    re.IGNORECASE,
)


def _normalize_name(name: str) -> str:
    return name.strip().strip("\"'").lower()


class CitationVerificationService:
    """
    Verifies that every inline [Source: filename chunk N] citation the
    LLM emits actually corresponds to a chunk that was retrieved for
    this answer. The LLM is instructed to only cite retrieved chunks,
    but nothing previously enforced that — it could (and, on smaller
    local models, does) fabricate a plausible-looking citation.

    This is a deterministic, non-LLM check (no extra latency/cost): it
    parses citation markers out of the answer and set-matches them
    against the known-good citation list built from the actual
    retrieval results.
    """

    def _known_citations(self, citations: list[str]) -> set[tuple[str, int]]:
        known = set()
        for c in citations or []:
            match = _KNOWN_RE.match(c.strip())
            if not match:
                continue
            known.add((_normalize_name(match.group("name")), int(match.group("chunk"))))
        return known

    def verify(self, answer: str, citations: list[str]) -> dict:
        """
        Returns:
            cleaned_answer: answer text with any fabricated citation
                markers stripped out (the surrounding sentence is kept —
                only the bracketed citation tag is removed).
            total: number of citation markers found in the answer.
            verified: number that matched a real retrieved chunk.
            hallucinated: number that matched nothing.
            hallucinated_citations: the raw fabricated marker text, for
                logging/debugging.
        """
        if not answer:
            return {
                "cleaned_answer": answer,
                "total": 0,
                "verified": 0,
                "hallucinated": 0,
                "hallucinated_citations": [],
            }

        known = self._known_citations(citations)
        matches = list(_CITATION_RE.finditer(answer))

        if not matches:
            return {
                "cleaned_answer": answer,
                "total": 0,
                "verified": 0,
                "hallucinated": 0,
                "hallucinated_citations": [],
            }

        verified = 0
        hallucinated = 0
        hallucinated_citations = []
        cleaned = answer

        # Walk matches in reverse so string offsets stay valid while we
        # strip out fabricated ones.
        for match in reversed(matches):
            key = (_normalize_name(match.group("name")), int(match.group("chunk")))

            if key in known:
                verified += 1
                continue

            hallucinated += 1
            hallucinated_citations.append(match.group(0))
            # Strip the fabricated citation tag but keep the sentence.
            cleaned = cleaned[: match.start()] + cleaned[match.end():]

        cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()

        total = verified + hallucinated

        log_debug(
            event="citation_verification",
            total=total,
            verified=verified,
            hallucinated=hallucinated,
        )
        if hallucinated:
            log_info(
                event="citation_hallucination_detected",
                hallucinated_citations=hallucinated_citations,
            )

        return {
            "cleaned_answer": cleaned,
            "total": total,
            "verified": verified,
            "hallucinated": hallucinated,
            "hallucinated_citations": hallucinated_citations,
        }


_citation_verifier = None


def get_citation_verification_service():
    global _citation_verifier

    if _citation_verifier is None:
        _citation_verifier = CitationVerificationService()

    return _citation_verifier
