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

    def add_chunk_view(
        self, chunk_id: int, view: str, embedding: list[float],
        document: str, metadata: dict
    ):
        """
        Store an additional retrieval "view" of an existing chunk
        (e.g. a summary or a set of hypothetical questions) under a
        composite id so it lives alongside the chunk's raw embedding
        without overwriting it. `metadata["chunk_id"]` and
        `metadata["view"]` let retrieval trace a view match back to the
        real chunk stored in the SQL database.
        """
        view_metadata = dict(metadata)
        view_metadata["chunk_id"] = chunk_id
        view_metadata["view"] = view

        self.collection.add(
            ids = [f"{chunk_id}:{view}"],
            embeddings = [embedding],
            documents = [document],
            metadatas = [view_metadata]
        )

    def search(self, query_embedding, top_k = 5, where = None):
        result = self.collection.query(
            query_embeddings = [query_embedding], 
            n_results = top_k,
            where = where
        )

        return result["ids"][0]