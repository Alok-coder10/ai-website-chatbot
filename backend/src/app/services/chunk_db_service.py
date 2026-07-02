import json
from sqlalchemy import select
from app.models.chunk import Chunk

class ChunkDBService:
    async def save(
        self, db, document_id, source_name, chunk_index, content, embedding
    ):
        chunk = Chunk(
            document_id = document_id,
            source_name = source_name,
            chunk_index = chunk_index,
            content = content,
            embedding = json.dumps(embedding)
        )

        db.add(chunk)
        await db.commit()
        await db.refresh(chunk)

        return chunk

    
    async def get_chunks(self, db, document_id):
        result = await db.execute(
            select(Chunk).where(
                Chunk.document_id == document_id
            )
        )

        return result.scalars().all()