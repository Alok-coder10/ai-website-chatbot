
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
)

from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class ParentDocument(Base, TimestampMixin):
    __tablename__ = "parent_documents"

    id = Column(
        Integer,
        primary_key=True,
    )

    document_id = Column(
        Integer,
        ForeignKey(
            "documents.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    parent_index = Column(Integer, nullable=False)

    title = Column(
        String(255),
        nullable=True,
    )

    text = Column(Text, nullable=False)

    document = relationship(
        "Document",
        back_populates="parents",
    )

    chunks = relationship(
        "Chunk",
        back_populates="parent",
        cascade="all, delete-orphan",
    )