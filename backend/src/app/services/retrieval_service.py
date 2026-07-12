
import json
import math

from app.services.chunk_db_service import ChunkDBService
from app.services.bm25_service import BM25Service
from app.services.document_db_service import DocumentDBService
from app.models import document
from app.vectordb.chroma_service import ChromaService
from app.cache.retrieval_cache import get_retrieval_cache

class RetrievalService:
    def __init__(self):
        self.chunk_db_service = ChunkDBService()
        self.bm25_service = BM25Service()
        self.document_db_service = DocumentDBService()
        self.chroma_service = ChromaService()
        self.retrieval_cache = get_retrieval_cache()

    
    async def hybrid_search(
        self, db, query, query_embedding,
        category = None, owner = None,  top_k = 8
    ):

        # -------------------------
        # Metadata filter for Chroma
        # -------------------------
        where = None
        if category and owner:
            where = {
                "$and": [
                    {"category": category},
                    {"owner": owner}
                ]
            }

        elif category:
            where = {
                "category": category
            }

        elif owner:
            where = {
                "owner": owner
            } 

        
        retcache_key = (
                f"{category}|"
                f"{owner}|"
                f"{query.strip().lower()}"
        )
        cached = self.retrieval_cache.get(retcache_key)

        if cached is not None:
            print("Retrieval Cache HIT")
            return cached

        print("Retrieval Cache MISS")


        # -------------------------
        # Semantic Search (Chroma)
        # -------------------------
        semantic = await self.retrieve(
            db=db,
            query_embedding=query_embedding,
            top_k=20,
            where=where
        )

        # -------------------------
        # BM25 Search
        # -------------------------
        keyword = (
            self.bm25_service.search(
                query,
                semantic,
                top_k = 20
            )
            if semantic
            else []
        )

        # -------------------------
        # Merge + Remove duplicates
        # -------------------------
        combined = semantic + keyword
        unique = {}

        for chunk in combined:
            unique[chunk.id] = chunk

        combined = list(unique.values())[:top_k]
        self.retrieval_cache.set(
            retcache_key, combined
        )

        return combined
 


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
        self, db, query_embedding, top_k = 20, where = None
    ):   
        
        ids = self.chroma_service.search(
            query_embedding=query_embedding,
            top_k= top_k,
            where = where
        )
        if not ids:
            return []
        
        ids = [int(i) for i in ids]

        return await self.chunk_db_service.get_chunks_by_ids(db, ids)




_retrieval_service = None

def get_retrieval_service():
    global _retrieval_service

    if _retrieval_service is None:
        _retrieval_service = RetrievalService()

    return _retrieval_service

        