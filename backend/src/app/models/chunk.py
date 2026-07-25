from sqlalchemy import(
    Column,
    Integer,
    String,
    ForeignKey,
    Text
)
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class Chunk(Base, TimestampMixin):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey( "documents.id"))
    source_name = Column(String)
    chunk_index = Column(Integer)
    content = Column(Text)
    embedding = Column(Text)
    parent_document_id = Column(
        Integer, 
        ForeignKey(
            "parent_documents.id", ondelete="CASCADE"
        ),
        index = True
    )
    document = relationship(
        "Document",
        back_populates="chunks"
    )
    parent = relationship(
        "ParentDocument",
        back_populates=  "chunks"
    )
