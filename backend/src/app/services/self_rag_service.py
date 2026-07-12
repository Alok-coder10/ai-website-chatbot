from app.llm.factory import get_llm_provider


class SelfRAGService:

    def __init__(self):
        self.provider = get_llm_provider()

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

        evidence = await self.provider.generate(
            prompt=prompt
        )
        
        if evidence.strip() == "NONE":
            decision = "NO"
        else:
            decision = "YES"

        return decision