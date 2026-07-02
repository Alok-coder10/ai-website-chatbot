from app.services import document_service, retrieval_service
from app.services import document_db_service
from app.services import chunk_db_service
from backend.src.app.schemas import document
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends
)
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.document_service import DocumentService
from app.services.document_db_service import DocumentDBService
from app.services.chunk_service import ChunkService
from app.services.chunk_db_service import ChunkDBService
from app.embeddings.embedder import Embedder
from app.services.retrieval_service import RetrievalService

router = APIRouter()
document_service = DocumentService()
document_db_service = DocumentDBService()
chunk_service = ChunkService()
chunk_db_service = ChunkDBService()
embedder = Embedder()
retrieval_service = RetrievalService()

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    path = await document_service.save_file(file)
    ext = Path(file.filename).suffix

    doc = await document_db_service.create(db, file.filename, ext)

    if ext == ".pdf":
        text = document_service.extract_pdf(path)
    elif ext == ".docx":
        text = document_service.extract_docx(path)
    else:
        text = document_service.extract_text(path)

    chunks = chunk_service.split(text)
    
    for i, c in enumerate(chunks):
        embedding = embedder.encode(c)
        await chunk_db_service.save(
            db = db,
            document_id= document.id,
            source_name = document.filename,
            chunk_index = i,
            content = c, 
            embedding = embedding
        )


    return {
        "id": doc.id,
        "filename": doc.filename,
        "path": path
    }


@router.get("/documetns")
async def list_documents(
    db: AsyncSession = Depends(get_db)
):
    return await document_db_service.list_documents(db)



@router.post(f"/documents/{id}/search")
async def search(
    document_id: int,
    query: str,
    db: AsyncSession = Depends(get_db)
):
    emb = embedder.encode(query)
    chunks = await retrieval_service.retrieve(db, document_id, emb)

    return [c.content for c in chunks]
