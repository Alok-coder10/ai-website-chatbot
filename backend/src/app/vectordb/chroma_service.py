from app.vectordb.chroma_client import client

class ChromaService:

    def __init__(self):
        self.collection = client.get_or_create_collection(
            name = "documents"
        )

        