from sentence_transformers import CrossEncoder
from app.core.logger import log_info

class Reranker:
    _model = None
    def __init__(self):
        if Reranker._model is None:
            Reranker._model = CrossEncoder(
                "cross-encoder/ms-marco-MiniLM-L-6-v2"
            )
        
        self.model = Reranker._model

    
    def rerank(self, query, chunks, top_k = 3):
        if not chunks:
            return []

        pairs = [
            (query, c.content ) for c in chunks
        ]

        scores = self.model.predict(pairs)
        ranked = list(zip(scores, chunks))

        ranked.sort(reverse=True, key= lambda x: x[0])

        for score, chunk in ranked[:5]:
            result = {
                "source": chunk.source_name,
                "chunk_index": chunk.chunk_index,
                "score": float(score),
                "preview": chunk.content[:120]
            }

            log_info(
                event = "Reranking",
                result = result
            )

        return [x[1] for x in ranked[:top_k]]