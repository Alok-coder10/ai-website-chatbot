from app.embeddings.model_loader import get_model
from app.cache.embedding_cache import get_embedding_cache
from app.core.config import settings

class Embedder:
    def __init__(self):
        self.model = get_model()
        self.cache = get_embedding_cache()

    def encode(self, text):
        print(f"Encodeing: {text}")

        if settings.ENABLE_QUERY_CACHE:
            cached = self.cache.get(text)
            if cached is not None:
                print("Embedding Cache HIT")
                return cached
        
        embedding = self.model.encode(text).tolist()
        if settings.ENABLE_QUERY_CACHE:
            self.cache.set(text, embedding)
            
        print("Embedding Cache MISS")
        return embedding


_embedder = Embedder()

def get_embedder():
    return _embedder