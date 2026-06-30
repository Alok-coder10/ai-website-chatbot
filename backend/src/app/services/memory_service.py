import json
from sqlalchemy import select
from app.models.memory import Memory

class MemoryService:
    async def save_memory(
            self,
            db,
            conversation_id,
            content,
            embedding
    ):
        memory = Memory(
            conversation_id=conversation_id,
            content=content,
            embedding=json.dumps(
                embedding
            )

        )
        db.add(memory)
        await db.commit()
        await db.refresh(memory)
        return memory

    async def get_memories(
            self,
            db,
            conversation_id
    ):
        result = await db.execute(
            select(Memory).where(
                Memory.conversation_id == conversation_id
            )
        )
        return result.scalars().all()
