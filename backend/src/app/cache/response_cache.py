class ResponseCache:

    def __init__(self):
        self.cache = {}

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value):
        self.cache[key] = value


_response_cache = None

def get_response_cache():
    global _response_cache

    if _response_cache is None:
        _response_cache = ResponseCache()

    return _response_cache