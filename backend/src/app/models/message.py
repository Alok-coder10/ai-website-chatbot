from sqlalchemy import(
    ForeignKey,
    Text
)
from sqlalchemy.orm import(
    Mapped,
    mapped_column,
    relationship,
)
from app.models.conversation import (
    Base,
    TimestampMixin
)

class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    role: Mapped[str]
    
    content: Mapped[str] = mapped_column(
        Text
    )

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey(
            "conversations.id"
        )
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )