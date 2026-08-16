from pydantic import BaseModel


class SummaryResponse(BaseModel):
    id: int
    conversation_id: int
    content: str

    class Config:
        from_attributes = True