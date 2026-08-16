from rank_bm25 import BM25Okapi

class BM25Service:

    def search(self, query, chunks, top_k=3):
        if not chunks:
            return []
        corpus = [c.content.split() for c in chunks]
        if len(corpus) == 0:
            return []
        bm25 = BM25Okapi(corpus)
        scores = bm25.get_scores(query.split())

        ranked = list(zip(scores, chunks))
        ranked.sort(reverse=True, key = lambda x: x[0])

        return [chunk for _, chunk in ranked[:top_k]]
