from sqlalchemy import(
    Column,
    Integer,
    String,
    ForeignKey,
    Text
)
from app.models.conversation import Base

class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey( "documents.id"))
    source_name = Column(String)
    chunk_index = Column(Integer)
    content = Column(Text)
    embedding = Column(Text)
