from app.vectordb.chroma_service import ChromaService

db = ChromaService()

print(db.collection.name)