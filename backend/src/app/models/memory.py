from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey
)
from app.models.base import Base, TimestampMixin

class Memory(Base, TimestampMixin):
    __tablename__ = "memories"
    id = Column(Integer, primary_key=True)
    conversation_id = Column(
        Integer,
        ForeignKey(
            "conversations.id"
        )
    )
    content = Column(Text)
    embedding = Column(Text)