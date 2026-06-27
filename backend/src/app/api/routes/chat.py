from fastapi import APIRouter
from app.schemas.chat import (
    ChatRequest,
    ChatResponse
)
from app.services.assistant_service import (
    AssistantService
)

router = APIRouter()
assistant = AssistantService()
@router.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(request: ChatRequest):
    response = await assistant.chat(request.message)
    return ChatResponse(response=response)
    