class QueryCache:

    def __init__(self):
        self.cache = {}

    def get(self, query: str):
        key = query.strip().lower()
        return self.cache.get(key)

    def set(self, query: str, expanded: str):
        key = query.strip().lower()
        self.cache[key] = expanded


_cache = QueryCache()


def get_query_cache():
    return _cache