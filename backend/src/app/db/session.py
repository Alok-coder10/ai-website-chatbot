from sqlalchemy.ext.asyncio import(
    AsyncSession, 
    async_sessionmaker
)
from app.db.database import engine

AsyncSessionLocal = async_sessionmaker(
    engine, 
    expire_on_commit=False,
    class_= AsyncSession
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session