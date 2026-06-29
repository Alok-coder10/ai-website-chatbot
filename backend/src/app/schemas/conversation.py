from datetime import datetime
from pydantic import BaseModel

class ConversationCreate(BaseModel):
    title: str = "New chat"

class conversationResponse(BaseModel):
    id: int
    uuid: str
    title: str
    created_at: datetime
    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime
    class Config:
        from_attributes = True