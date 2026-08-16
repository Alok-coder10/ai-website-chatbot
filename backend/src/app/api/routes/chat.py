from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.assistant_service import AssistantService

router = APIRouter()
assistant = AssistantService()


# -----------------------------
# Existing JSON endpoint
# -----------------------------
@router.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await assistant.chat(
        db,
        request.message,
        request.conversation_id,
        request.category,
        request.owner,
    )

    return ChatResponse(
        conversation_id=result["conversation_id"],
        response=result["response"],
    )


# -----------------------------
# Streaming generator
# -----------------------------
async def stream_generator(
    db,
    message,
    conversation_id,
    category,
    owner,
):
    async for token in assistant.chat_stream(
        db=db,
        message=message,
        conversation_id=conversation_id,
        category=category,
        owner=owner,
    ):
        yield token


# -----------------------------
# Streaming endpoint
# -----------------------------
@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    return StreamingResponse(
        stream_generator(
            db,
            request.message,
            request.conversation_id,
            request.category,
            request.owner,
        ),
        media_type="text/plain",
    )