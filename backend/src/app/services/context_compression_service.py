class ContextCompressionService:
    """
    Compress retrieved context before it is passed to the LLM.

    The first implementation keeps this deterministic and lightweight:
    - removes empty content
    - removes duplicate text
    - limits individual parent documents
    - limits the total context size
    """

    MAX_PARENT_CHARS = 6000
    MAX_CONTEXT_CHARS = 16000

    def compress(self, contexts: list[str]) -> list[str]:
        if not contexts:
            return []

        compressed = []
        seen = set()
        total_chars = 0

        for context in contexts:
            if not context:
                continue

            context = context.strip()

            if not context:
                continue

            # Remove duplicate contexts
            normalized = context.lower()

            if normalized in seen:
                continue

            seen.add(normalized)

            # Limit individual parent context
            if len(context) > self.MAX_PARENT_CHARS:
                context = context[:self.MAX_PARENT_CHARS]

            # Respect total context budget
            remaining = self.MAX_CONTEXT_CHARS - total_chars

            if remaining <= 0:
                break

            if len(context) > remaining:
                context = context[:remaining]

            compressed.append(context)
            total_chars += len(context)

        return compressed


_context_compression_service = None


def get_context_compression_service():
    global _context_compression_service

    if _context_compression_service is None:
        _context_compression_service = ContextCompressionService()

    return _context_compression_service