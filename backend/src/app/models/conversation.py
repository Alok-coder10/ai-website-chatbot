import uuid
from sqlalchemy.orm import(
    Mapped,
    mapped_column,
    relationship,
    DeclarativeBase
)
from sqlalchemy import String
from app.models.base import(
    Base,
    TimestampMixin
)

class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )
    uuid: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        default=lambda: str(uuid.uuid4())
    )

    title: Mapped[str] = mapped_column(
        String(255)
    )

    messages = relationship(
        "Message", 
        back_populates="conversation",
        cascade="all, delete"
    )
