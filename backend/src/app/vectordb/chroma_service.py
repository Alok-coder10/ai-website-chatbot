from app.vectordb.chroma_client import client

class ChromaService:

    def __init__(self):
        self.collection = client.get_or_create_collection(
            name = "documents"
        )

    def add_chunks(
        self, chunk_id: int, embedding: list[float], 
        document: str, metadata: dict
    ):
        self.collection.add(
            ids  =[str(chunk_id)], 
            embeddings = [embedding],
            documents = [document],
            metadatas = [metadata]
        )

    def search(self, query_embedding, top_k = 5, where = None):
        result = self.collection.query(
            query_embeddings = [query_embedding], 
            n_results = top_k,
            where = where
        )

        return result["ids"][0]