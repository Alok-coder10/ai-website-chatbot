import json
from sqlalchemy import select
from app.models.chunk import Chunk

class ChunkDBService:
    async def save(
        self, db, document_id, content, embedding
    ):
        chunk = Chunk(
            document_id = document_id,
            content = content,
            embeddings = json.dumps(embedding)
        )

        db.add(chunk)
        await db.commit()
        await db.refresh(chunk)

        return chunk

    
    async def get_chunks(self, db, document_id):
        result = await db.execute(
            select(chunk).where(
                chunk.document_id == document_id
            )
        )

        return result.scalars().all()