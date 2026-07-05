import json
import math
from app.services.chunk_db_service import ChunkDBService
from app.services.bm25_service import BM25Service
from app.services.document_db_service import DocumentDBService
from app.models import document

class RetrievalService:
    def __init__(self):
        self.chunk_db_service = ChunkDBService()
        self.bm25_service = BM25Service()
        self.document_db_service = DocumentDBService()

    
    async def hybrid_search(
        self, db, query, query_embedding,
        category = None, owner = None,  top_k = 8
    ):

        documents = await (
            self.document_db_service.filter_documents(
                db, category, owner
            )
        )

        #debugging

        print("FILTERED DOCS")
        for d in documents:
            print(d.id, d.filename, d.category, d.owner)


        if category or owner:
            ids = [d.id for d in documents]

            #debuging
            print(ids)
            

            if ids:
                chunks = await (
                    self.chunk_db_service.get_chunks_by_document_ids(db, ids)
                )
            
            else:
                chunks = []


            #debugging
            print("CHUNK count", len(chunks))

            for c in chunks:
                print(
                    c.document_id,
                    c.source_name
                )




        else:
            chunks = await (
                self.chunk_db_service.get_all_chunks(db)
            )
            
        semantic = []
        keyword = []
        if chunks:
            semantic = await self.retrieve(chunks , query_embedding, top_k) 
            keyword = (
                self.bm25_service.search(query, chunks, top_k) or []
            )

        results = {}
        for c in semantic:
            results[c.id] = c
        
        for c in keyword:
            results[c.id] = c

        combined = semantic + keyword
        seen = {}

        for c in combined:
            seen[c.id] = c
        
        combined = list(seen.values())

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
        self, chunks, query_embedding, top_k = 8
    ):   
        scored = []
        for c in chunks:
            emb = json.loads(c.embedding)

            score = self.cosine_similarity(query_embedding, emb)
            scored.append((score, c))

        scored.sort(reverse=True, key=lambda x:x[0])

        return [x[1] for x in scored[:top_k]]

        