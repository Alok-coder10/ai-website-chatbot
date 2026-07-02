from sqlalchemy import(
    Column,
    Integer,
    ForeignKey,
    Text
)
from app.models.conversation import Base

class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey( "documents.id"))
    content = Column(Text)
    embedding = Column(Text)
