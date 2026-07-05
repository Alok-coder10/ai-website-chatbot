from sqlalchemy import select
from app.models.document import Document

class DocumentDBService:
    
    async def create(
        self, db, filename, filetype, category = None, owner = None, tags = None
    ):
        doc = Document(
            filename=filename, filetype=filetype, category = category,
            owner = owner,
            tags = tags
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        return doc

    async def list_documents(self, db):
        result = await db.execute(
            select(Document)
        )
        return result.scalars().all()


    async def filter_documents(
        self, db, category = None, owner = None
    ):
        query = select(Document)

        if category:
            query = query.where(
                Document.category == category
            )
        
        if owner:
            query = query.where(
                Document.owner == owner
            )
        
        result = await db.execute(query)
        return result.scalars().all()

    
    