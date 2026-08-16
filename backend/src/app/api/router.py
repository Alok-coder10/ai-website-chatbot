from __future__ import annotations
from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.chat import router as chat_router
from app.api.routes import conversations
from app.api.routes.document import router as document_router
from app.api.routes.metrics import router as metrics_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["Health"])
api_router.include_router(chat_router, tags=["Chat"])

api_router.include_router(
    conversations.router, 
    tags=["Conversations"]
)

api_router.include_router(
    document_router,
    tags=["RAG Services"]
)

api_router.include_router(
    metrics_router,
    tags = ["Metrices"]
)

