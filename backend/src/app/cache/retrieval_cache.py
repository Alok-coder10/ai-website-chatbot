class RetrievalCache:

    def __init__(self):
        self.cache = {}

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value):
        self.cache[key] = value
    
    def health_check(self) -> bool:
        return True


_retrieval_cache = None

def get_retrieval_cache():
    global _retrieval_cache

    if _retrieval_cache is None:
        _retrieval_cache = RetrievalCache()

    return _retrieval_cache