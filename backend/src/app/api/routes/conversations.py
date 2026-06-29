from fastapi import(
    APIRouter,
    Depends,
    HTTPException
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.conversation_service import (
    ConversationService
)
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse
)

router = APIRouter()
service = ConversationService()


@router.post("/conversations", response_model=ConversationResponse)

async def create_conversation(
    data: ConversationCreate, 
    db: AsyncSession = Depends(get_db)
):

    conversation = await service.create_conversation(db, data.title)
    return conversation

@router.get("/conversations", response_model=list[ConversationResponse])

async def list_conversations(
    db: AsyncSession = Depends(get_db)
):
    return await service.list_conversations(db)

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    conversation = await service.get_conversation(db, conversation_id)
    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )
    return conversation


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    deleted = await service.delete_conversation(db, conversation_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )
    return {
        "message":
        "Conversation deleted"
    }