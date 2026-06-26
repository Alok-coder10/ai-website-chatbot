from __future__ import annotations
from fastapi import APIRouter
from app.schemas.response import ApiResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=ApiResponse,
)
async def health_check():
    return ApiResponse(
        success=True,
        message="API is healthy",
        data={
            "status": "healthy",
        },
    )