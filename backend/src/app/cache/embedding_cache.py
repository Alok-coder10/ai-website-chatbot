class EmbeddingCache:

    def __init__(self):
        self.cache = {}

    def get(self, text: str):
        key = text.strip().lower()
        return self.cache.get(key)

    def set(self, text: str, embedding):
        key = text.strip().lower()
        self.cache[key] = embedding


_cache = EmbeddingCache()


def get_embedding_cache():
    return _cache