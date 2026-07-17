from app.llm.factory import get_llm_provider

class ResponseValidationService:
    def __init__(self):
        self.provider = get_llm_provider()

    async def validate(
        self, question: str, context: str, answer: str,
    ) -> bool:

        prompt = f"""
You are verifying an answer produced by a Retrieval-Augmented Generation (RAG) system.

Question:
{question}

Retrieved Documents:
{context}

Generated Answer:
{answer}

Task:

Evaluate every factual claim in the generated answer.

For each claim determine whether it is directly supported by the retrieved documents.

Rules:

- If every claim is supported, return:

SUPPORTED

- Otherwise return:

UNSUPPORTED

Unsupported Claims:
- claim 1
- claim 2
- ...

Never invent unsupported claims.

Never explain.

Never rewrite the answer.

Return ONLY the required format.
"""

        result = (await self.provider.generate(prompt)).strip()
        supported = result.upper().startswith("SUPPORTED")

        return {
            "supported": supported,
            "report": result
        }

_validator = None

def get_response_validation_service():
    global _validator

    if _validator is None:
        _validator = ResponseValidationService()

    return _validator