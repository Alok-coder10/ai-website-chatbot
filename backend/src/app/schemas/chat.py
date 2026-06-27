from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    """
    Incoming chat request
    """
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User message"
    )

class ChatResponse(BaseModel):
    """
    Assistant response
    """

    response: str