from app.reranker.reranker import Reranker

_reranker = None

def get_reranker():
    global _reranker

    if _reranker is None:
        _reranker = Reranker()

    return _reranker