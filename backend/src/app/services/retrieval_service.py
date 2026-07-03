import json
import math
from app.services.chunk_db_service import ChunkDBService
from app.services.bm25_service import BM25Service

class RetrievalService:
    def __init__(self):
        self.chunk_db_service = ChunkDBService()
        self.bm25_service = BM25Service()

    
    async def hybrid_search(
        self, db, query, query_embedding, top_k = 3
    ):
        chunks = await self.chunk_db_service.get_all_chunks(db)
        semantic = []
        keyword = []
        if chunks:
            semantic = await self.retrieve(db, None, query_embedding, top_k)
            keyword = (
                self.bm25_service.search(query, chunks, top_k) or []
            )

        results = {}
        for c in semantic:
            results[c.id] = c
        
        for c in keyword:
            results[c.id] = c

        combined = list(results.values())

        return combined[:top_k]


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
        if document_id:
            chunks = await self.chunk_db_service.get_chunks(db, document_id)
        
        else:
            chunks = await self.chunk_db_service.get_all_chunks(db)
        
        scored = []
        for c in chunks:
            emb = json.loads(c.embedding)

            score = self.cosine_similarity(query_embedding, emb)
            scored.append((score, c))

        scored.sort(reverse=True, key=lambda x:x[0])

        return [x[1] for x in scored[:top_k]]

        