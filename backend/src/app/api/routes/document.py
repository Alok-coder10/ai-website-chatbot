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

router = APIRouter()
service = DocumentService()
db_service = DocumentDBService()

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    path = await service.save_file(file)
    ext = Path(file.filename).suffix

    doc = await db_service.create(db, file.filename, ext)

    return {
        "id": doc.id,
        "filename": doc.filename,
        "path": path
    }


@router.get("/documetns")
async def list_documents(
    db: AsyncSession = Depends(get_db)
):
    return await db_service.list_documents(db)