from sqlalchemy import(
    Column,
    Integer,
    String,
    Text,
    DateTime,
)
from datetime import datetime
from app.models.conversation import Base

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    filetype = Column(String)
    category = Column(String)
    owner = Column(String)
    tags = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


