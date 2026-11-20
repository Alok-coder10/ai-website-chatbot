from sqlalchemy import(
    Column,
    Integer,
    String,
    Text,
    DateTime,
)
from datetime import datetime

from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class Document(Base, TimestampMixin):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    filetype = Column(String)
    category = Column(String)
    owner = Column(String)
    tags = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    parents = relationship(
        "ParentDocument",
        back_populates="document",
        cascade="all, delete-orphan"
    )
    chunks = relationship(
        "Chunk",
        back_populates="document",
        cascade="all, delete-orphan"
    )


