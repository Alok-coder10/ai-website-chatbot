from contextlib import contextmanager
from sqlalchemy import select
from app.models.summary import Summary

class SummaryService:
    async def get_summary(self, db, conversation_id):
        result = await db.execute(
            select(Summary).where(
                Summary.conversation_id
                == conversation_id
            )
        )
        return result.scalar_one_or_none()

    async def save_summary(
        self,
        db,
        conversation_id,
        content
    ):
        summary = Summary(
            conversation_id=conversation_id,
            content=content
        )

        db.add(summary)
        await db.commit()
        await db.refresh(summary)
        return summary
    
    async def update_summary(
        self, db, summary, content
    ):
        summary.content = content
        await db.commit()
        await db.refresh(summary)
        return summary