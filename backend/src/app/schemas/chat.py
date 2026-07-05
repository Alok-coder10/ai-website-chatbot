from pydantic import BaseModel, Field, field_validator

class ChatRequest(BaseModel):
    """
    Incoming chat request
    """
    message: str
    conversation_id: int | None = None
    category: str | None = None
    owner: str | None = None

    @field_validator("message")
    @classmethod
    def validate_message(cls, value):
        if not value.strip():
            raise ValueError("Message cannot be empty")
        return value

class ChatResponse(BaseModel):
    """
    Assistant response
    """
    conversation_id: int
    response: str