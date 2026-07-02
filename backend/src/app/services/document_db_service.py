from sqlalchemy import select
from app.models.document import Document

class DocumentDBService:
    
    async def create(
        self, db, filename, filetype
    ):
        doc = Document(filename=filename, filetype=filetype)
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        return doc

    async def list_documents(self, db):
        result = await db.execute(
            select(Document)
        )
        return result.scalars().all()

    
    