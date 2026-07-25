from sqlalchemy import select
from app.models.parent_document import ParentDocument
from sqlalchemy import select
from sqlalchemy.orm import selectinload

class ParentDocumentDBService:
    async def get_by_ids(
        self,
        db,
        ids,
    ):
        if not ids:
            return []

        result = await db.execute(
            select(ParentDocument).options(
                selectinload(ParentDocument.document)).where(
                ParentDocument.id.in_(ids)
            )
        )

        parents = result.scalars().all()

        parent_map = {
            p.id: p
            for p in parents
        }

        return [
            parent_map[i]
            for i in ids
            if i in parent_map
        ]