from app.embeddings.model_loader import get_model
from app.cache.embedding_cache import get_embedding_cache
from app.core.config import settings
from app.core.logger import log_debug, log_info


class Embedder:
    def __init__(self):
        self.model = get_model()
        self.cache = get_embedding_cache()

    def encode(self, text:str):
        log_info(
            event="Encoding text:",
            result = text
        )
        
        if settings.ENABLE_QUERY_CACHE:
            cached = self.cache.get(text)
            if cached is not None:
                log_debug(
                    event = "cache_hit",
                    cache = "embedding"
                )
                return cached
        
        embedding = self.model.encode(text).tolist()
        if settings.ENABLE_QUERY_CACHE:
            self.cache.set(text, embedding)
            
        log_debug(
            event = "cache_miss",
            cache = "embedding"
        )
        return embedding

    def encode_batch(self, texts: list[str]):
        embeddings = []
        uncached_texts = []
        uncached_indices = []

        for i, text in enumerate(texts):
            if settings.ENABLE_QUERY_CACHE:
                cached = self.cache.get(text)

                if cached is not None:
                    embeddings.append(cached)
                    continue
            
            embeddings.append(None)
            uncached_texts.append(text)
            uncached_indices.append(i)
        
        if uncached_texts:
            new_embeddings = (
                self.model.encode(uncached_texts).tolist()
            )

            for idx, embedding, text in zip(
                uncached_indices, new_embeddings, uncached_texts
            ):
                embeddings[idx] = embedding
                if settings.ENABLE_QUERY_CACHE:
                    self.cache.set(text, embedding)
        
        return embeddings



_embedder = Embedder()

def get_embedder():
    return _embedder