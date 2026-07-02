import json
import math
from app.services.chunk_db_service import ChunkDBService

class RetrievalService:
    def __init__(self):
        self.chunk_db_service = ChunkDBService()

    def cosine_similarity(self, a, b):
        dot = sum(x*y for x, y in zip(a,b))
        norm_a = math.sqrt(
            sum(
                x*x for x in a
            )
        )
        norm_b = math.sqrt(
            sum(
                x*x for x in b
            )
        )

        if norm_a == 0 or norm_b == 0:
            return 0
        
        return dot/(norm_a * norm_b)

    async def retrieve(
        self, db, document_id, query_embedding, top_k = 3
    ):
        chunks = await self.chunk_db_service.get_chunks(db, document_id)
        
        scored = []
        for c in chunks:
            emb = json.loads(c.embedding)

            score = self.cosine_similarity(query_embedding, emb)
            scored.append((score, c))

        scored.sort(reverse=True, key=lambda x:x[0])

        return [x[1] for x in scored[:top_k]]

        