from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.core.exceptions import register_exception_handlers
from app.core.middleware import log_requests



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown events.
    """

    setup_logging()

    logger.info(f"Starting {settings.app_name}...")
    logger.info(f"Environment: {'Development' if settings.debug else 'Production'}")

    yield

    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

register_exception_handlers(app)

app.middleware("http")(log_requests)

# ----------------------------
# Middleware
# ----------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Routers
# ----------------------------

app.include_router(
    api_router,
    prefix=settings.api_v1_prefix,
)


# ----------------------------
# Root Endpoint
# ----------------------------


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    return {
        "message": f"Welcome to {settings.app_name}",
    }