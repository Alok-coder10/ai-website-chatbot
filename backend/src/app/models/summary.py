from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text
)
from app.models.conversation import Base

class Summary(Base):
    __tablename__ = "summaries"
    id = Column(Integer, primary_key=True)

    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id"),
        unique=True
    )
    content = Column(Text)