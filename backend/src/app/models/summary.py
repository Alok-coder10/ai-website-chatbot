from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text
)
from app.models.base import Base, TimestampMixin

class Summary(Base, TimestampMixin):
    __tablename__ = "summaries"
    id = Column(Integer, primary_key=True)

    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id"),
        unique=True
    )
    content = Column(Text)