from __future__ import annotations
from datetime import datetime, timezone
from backend.src.app.services import database_health_service
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.runtime import START_TIME
from app.llm.factory import get_llm_provider
from fastapi import APIRouter
from app.schemas.response import ApiResponse
from app.cache.embedding_cache import get_embedding_cache
from app.cache.prompt_cache import get_prompt_cache
from app.cache.query_cache import get_query_cache
from app.cache.response_cache import get_response_cache
from app.cache.retrieval_cache import get_retrieval_cache
from app.db.session import get_db
from app.services.database_health_service import get_database_health_service


router = APIRouter(tags=["Health"])

@router.get(
    "/ready",
    response_model = ApiResponse
)
async def readiness_check(
    db: AsyncSession = Depends(get_db)
):
    provider = get_llm_provider()
    database_health = get_database_health_service()
    response_cache = get_response_cache()
    embedding_cache = get_embedding_cache()
    query_cache = get_query_cache()
    prompt_cache = get_prompt_cache()
    retrieval_cache = get_retrieval_cache()

    cache_status = {
        "response": response_cache.health_check(),
        "embedding": embedding_cache.health_check(),
        "query_expansion": query_cache.health_check(),
        "prompt": prompt_cache.health_check(),
        "retrieval": retrieval_cache.health_check()
    }

    provider_ok = await provider.health_check()
    database_ok = await database_health.database_health(db)

    ready = (
        provider_ok and database_ok and all(cache_status.values())
    )

    return ApiResponse(
        success=ready,
        message=(
            "Application ready" if ready else "Application not ready"
        ),
        data = {
            "ready": ready,
            "provider": provider_ok,
            "database": database_ok,
            "cache": cache_status
        }
    )


@router.get(
    "/health",
    response_model=ApiResponse,
)
async def health_check(db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc)
    uptime = (
        now - START_TIME
    ).total_seconds()

    provider_ok = await get_llm_provider().health_check()

    response_cache = get_response_cache()
    embedding_cache = get_embedding_cache()
    query_cache = get_query_cache()
    prompt_cache = get_prompt_cache()
    retrieval_cache = get_retrieval_cache()
    database_health = get_database_health_service()
    
    database_ok = await database_health.database_health(db)
    

    cache_status = {
        "response": response_cache.health_check(),
        "embedding": embedding_cache.health_check(),
        "query_expansion": query_cache.health_check(),
        "prompt": prompt_cache.health_check(),
        "retrieval": retrieval_cache.health_check()
    }

    overall_status = (
        "healthy"
        if (provider_ok and database_ok and all(cache_status.values()))
        else "degraded"
    )

    return ApiResponse(
        success= True,
        message="API is healthy",
        data={
            "status": overall_status,
            "provider": {
                "status": (
                    "healthy" if provider_ok else "unavailable"
                )
            },
            "database": {
                "status": "healthy" if database_ok else "unavailable"
            },
            "cache": {
                "response": "healthy" if cache_status["response"] else "failed",
                "embedding": "healthy" if cache_status["embedding"] else "failed",
                "query_expansion": "healthy" if cache_status["query_expansion"] else "failed",
                "prompt": "healthy" if cache_status["prompt"] else "failed",
                "retrieval": "healthy" if cache_status["retrieval"] else "failed"
            },
            "version": "1.0.0",
            "uptime_seconds": round(uptime, 2),
            "timestamp": now.isoformat()
        },
    )