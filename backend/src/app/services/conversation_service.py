from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conversation import Conversation
from app.models.message import Message

class ConversationService:
    async def create_conversation(
        self, 
        db: AsyncSession, 
        title: str = "New Chat"
    ) -> Conversation:

        conversation = Conversation(
            title=title
        )

        db.add(
            conversation
        )

        await db.commit()
        await db.refresh(
            conversation
        )
        return conversation


    async def save_message(
        self,
        db: AsyncSession,
        conversation_id: int,
        role: str,
        content: str
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )

        db.add(
            message
        )

        await db.commit()
        await db.refresh(
            message
        )

        return message

    async def get_messages(
        self,
        db: AsyncSession,
        conversation_id: int
    ):
        result = await db.execute(
            select(Message)
            .where(
                Message.conversation_id
                == conversation_id
            )
        )
        return result.scalars().all()