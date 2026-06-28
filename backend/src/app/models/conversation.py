from email import message
from sqlalchemy.orm import(
    Mapped,
    mapped_column,
    relationship,
    DeclarativeBase
)
from sqlalchemy import String

class Base(DeclarativeBase):
    pass

class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    title: Mapped[str] = mapped_column(
        String(255)
    )

    messages = relationship("Message", back_populates="conversation")
    