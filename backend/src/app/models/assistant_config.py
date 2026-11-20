import uuid

from sqlalchemy import Boolean, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class AssistantConfig(Base, TimestampMixin):
    """Configuration for an individual website assistant."""

    __tablename__ = "assistant_configs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    uuid: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        index=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        default="My Assistant",
    )

    system_prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="You are a helpful website assistant. Answer clearly and accurately.",
    )

    llm_provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="ollama",
    )

    llm_model: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        default="llama3.2:3b",
    )

    temperature: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.2,
    )

    max_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1024,
    )

    welcome_message: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        default="Hi! How can I help you today?",
    )

    primary_color: Mapped[str] = mapped_column(
        String(7),
        nullable=False,
        default="#2563EB",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )