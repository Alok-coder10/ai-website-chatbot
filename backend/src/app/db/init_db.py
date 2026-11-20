import asyncio
from app.db.database import engine
from app.models.conversation import Base
from app.models.summary import Summary
from app.models.memory import Memory
from app.models.document import Document
from app.models.chunk import Chunk

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.create_all
        )

if __name__ == "__main__":
    asyncio.run(init_db())