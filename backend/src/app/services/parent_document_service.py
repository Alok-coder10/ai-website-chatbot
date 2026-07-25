from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parent_document import ParentDocument
from app.services.parent_document_db_service import ParentDocumentDBService


class ParentDocumentService:
    def __init__(self):
        self.parent_db_service = ParentDocumentDBService()

    async def create_parent_document(
        self,
        db: AsyncSession,
        document_id: int,
        parent_index: int,
        text: str,
        title: str | None = None,
    ) -> ParentDocument:

        parent = ParentDocument(
            document_id=document_id,
            parent_index=parent_index,
            title=title,
            text=text,
        )

        db.add(parent)

        await db.commit()
        await db.refresh(parent)

        return parent


    async def get_parent_document(
        self,
        db: AsyncSession,
        parent_document_id: int,
    ) -> ParentDocument | None:

        result = await db.execute(
            select(ParentDocument).where(
                ParentDocument.id == parent_document_id
            )
        )

        return result.scalar_one_or_none()


    async def get_parent_documents(
        self,
        db: AsyncSession,
        document_id: int,
    ) -> list[ParentDocument]:

        result = await db.execute(
            select(ParentDocument).where(
                ParentDocument.document_id == document_id
            ).order_by(
                ParentDocument.parent_index
            )
        )

        return list(result.scalars().all())


    async def update_parent_document(
        self,
        db: AsyncSession,
        parent_document_id: int,
        title: str | None = None,
        text: str | None = None,
    ) -> ParentDocument | None:

        parent = await self.get_parent_document(
            db,
            parent_document_id,
        )

        if parent is None:
            return None

        if title is not None:
            parent.title = title

        if text is not None:
            parent.text = text

        await db.commit()
        await db.refresh(parent)

        return parent


    async def delete_parent_document(
        self,
        db: AsyncSession,
        parent_document_id: int,
    ) -> bool:

        parent = await self.get_parent_document(
            db,
            parent_document_id,
        )

        if parent is None:
            return False

        await db.delete(parent)
        await db.commit()

        return True

    