from backend.src.app.services import document_service
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

router = APIRouter()
service = DocumentService()
document_db = DocumentDBService()
chunk_service = ChunkService()
chunk_db = ChunkDBService()
embedder = Embedder()

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    path = await service.save_file(file)
    ext = Path(file.filename).suffix

    doc = await document_db.create(db, file.filename, ext)

    if ext == ".pdf":
        text = document_service.extract_pdf(path)
    elif ext == ".docx":
        text = document_service.extract_docx(path)
    else:
        text = document_service.extract_text(path)

    chunks = chunk_service.split(text)
    
    for c in chunks:
        embedding = embedder.encode(c)
        await chunk_db.save(
            db, doc.id, c, embedding
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
    return await document_db.list_documents(db)