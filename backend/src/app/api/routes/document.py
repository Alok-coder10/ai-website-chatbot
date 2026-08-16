
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
from app.embeddings.embedder import get_embedder
from app.services.retrieval_service import get_retrieval_service
from app.vectordb.chroma_service import ChromaService
from app.services.parent_document_db_service import ParentDocumentDBService
from app.services.parent_split_service import get_parent_split_service
from app.services.parent_document_service import ParentDocumentService

router = APIRouter()
document_service = DocumentService()
document_db_service = DocumentDBService()
chunk_service = ChunkService()
chunk_db_service = ChunkDBService()
embedder = get_embedder()
retrieval_service = get_retrieval_service()
chroma_service = ChromaService()
parent_split_service = get_parent_split_service()
parent_document_db_service = ParentDocumentDBService()
parent_document_service = ParentDocumentService()

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    category: str | None = None,
    owner: str | None = None,
    tags: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    path = await document_service.save_file(file)
    ext = Path(file.filename).suffix

    doc = await document_db_service.create(
        db, file.filename, ext,
        category, owner, tags
    )

    if ext == ".pdf":
        text = document_service.extract_pdf(path)
    elif ext == ".docx":
        text = document_service.extract_docx(path)
    else:
        text = document_service.extract_text(path)

    parents = parent_split_service.split(text)
    chunk_index = 0
    
    for parent_index, parent_text in enumerate(parents):
        parent = await parent_document_service.create_parent_document(
            db = db,
            document_id= doc.id,
            parent_index= parent_index,
            text = parent_text
        )

        child_chunks = chunk_service.split(parent_text)

        for child in child_chunks:
            embedding = embedder.encode(child)

            chunk = await chunk_db_service.save(
                db = db,
                document_id= doc.id,
                parent_document_id= parent.id,
                source_name= doc.filename,
                chunk_index= chunk_index,
                content = child,
                embedding=embedding
            )

            chroma_service.add_chunks(
                chunk_id= chunk.id,
                embedding= embedding,
                document = child,
                metadata={
                    "document_id": doc.id,
                    "parent_document_id": parent.id,
                    "filename": doc.filename,
                    "category": category or "",
                    "owner": owner or "",
                    "chunk_index": chunk_index
                }
            )

            chunk_index +=1

    # print(chroma_service.count())
    return {
        "id": doc.id,
        "filename": doc.filename,
        "path": path
    }


@router.get("/documents")
async def list_documents(
    db: AsyncSession = Depends(get_db)
):
    return await document_db_service.list_documents(db)



@router.post("/documents/{document_id}/search")
async def search(
    document_id: int,
    query: str,
    db: AsyncSession = Depends(get_db)
):
    emb = embedder.encode(query)
    chunks = await retrieval_service.retrieve(db, document_id, emb)

    return [c.content for c in chunks]
