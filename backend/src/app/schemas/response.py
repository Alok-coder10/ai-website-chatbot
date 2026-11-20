from pydantic import BaseModel

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: dict | list | None = None

class ChatResponse(BaseModel):
    conversation_id: int
    response: str