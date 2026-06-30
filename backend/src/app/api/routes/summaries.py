from fastapi import(
    APIRouter,
    Depends,
    HTTPException
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.summary_service import SummaryService

router = APIRouter()
service = SummaryService()

@router.get("/conversations/{id}/summary")
async def get_summary(
    id:int,
    db:AsyncSession
):
    return await service.get_summary(
        db,
        id
    )