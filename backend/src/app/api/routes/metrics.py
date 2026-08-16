from fastapi import APIRouter

from app.schemas.response import ApiResponse
from app.services.metrics_service import get_metrics_service

router = APIRouter()

@router.get(
    "/metrics",
    response_model=ApiResponse,
)
async def get_metrics():

    return ApiResponse(
        success=True,
        message="Metrics collected successfully",
        data=get_metrics_service().get_stats()
    )