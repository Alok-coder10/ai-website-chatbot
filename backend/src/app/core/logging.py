from __future__ import annotations
import sys
from app.core.config import settings
from loguru import logger

def setup_logging() -> None:
    """
    Configure the application logger.
    """

    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.log_level,
        colorize=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
    )

__all__ = ["logger", "setup_logging"]