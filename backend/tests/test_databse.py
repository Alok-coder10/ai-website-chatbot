from sqlalchemy import inspect
from app.db.database import engine
import asyncio

async def get_tables():
    async with engine.begin() as conn:
        return await conn.run_sync(
            lambda sync_conn:
            inspect(sync_conn).get_table_names()
        )

def test_tables_exist():
    tables = asyncio.run(get_tables())

    assert "conversations" in tables
    assert "messages" in tables