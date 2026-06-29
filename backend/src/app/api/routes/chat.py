from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from fastapi import(
    APIRouter,
    Depends
)
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
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)    
):
    result = await assistant.chat(db, request.message, request.conversation_id)
    return ChatResponse(
        conversation_id = result["conversation_id"],
        response = result["response"]
    )
    