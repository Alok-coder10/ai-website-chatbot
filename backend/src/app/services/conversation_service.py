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

        conversation = Conversation(title=title)
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
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

        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message

    async def get_messages(
        self,
        db,
        conversation_id: int
    ):
        result = await db.execute(
            select(Message).where(
                Message.conversation_id == conversation_id
            ).order_by(
                Message.created_at
            )
        )
        return result.scalars().all()

    async def get_conversation(self, db, conversation_id: int):
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id
            )
        )
        return result.scalar_one_or_more()

    async def list_conversations(self, db):
        result = await db.execute(
            select(Conversation)
        )
        return result.scalars().all()

    async def delete_conversation(self, db, conversation_id: int):
        conversation = await self.get_conversation(db, conversation_id)
        if not conversation:
            return False
        
        await db.delete(conversation)
        await db.commit()
        return True