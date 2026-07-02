from sqlalchemy import(
    Column,
    Integer,
    String,
    DateTime,
)
from datetime import datetime
from app.models.conversation import Base

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    filetype = Column(String)
    created_at = Column(DateTime, default=datetime.now)


