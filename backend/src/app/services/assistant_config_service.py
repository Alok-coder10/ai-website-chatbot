from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assistant_config import AssistantConfig
from app.schemas.assistant_config import (
    AssistantConfigCreate,
    AssistantConfigUpdate,
)


async def create_assistant_config(
    db: AsyncSession,
    payload: AssistantConfigCreate,
) -> AssistantConfig:
    """Create a new assistant configuration."""
    config = AssistantConfig(**payload.model_dump())

    db.add(config)
    await db.commit()
    await db.refresh(config)

    return config


async def get_assistant_config_by_uuid(
    db: AsyncSession,
    config_uuid: str,
) -> AssistantConfig | None:
    """Fetch an assistant configuration by UUID."""
    result = await db.execute(
        select(AssistantConfig).where(
            AssistantConfig.uuid == config_uuid
        )
    )
    return result.scalar_one_or_none()


async def list_assistant_configs(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
) -> list[AssistantConfig]:
    """List assistant configurations with basic pagination."""
    result = await db.execute(
        select(AssistantConfig)
        .order_by(AssistantConfig.id.desc())
        .offset(skip)
        .limit(min(max(limit, 1), 100))
    )
    return list(result.scalars().all())


async def update_assistant_config(
    db: AsyncSession,
    config: AssistantConfig,
    payload: AssistantConfigUpdate,
) -> AssistantConfig:
    """Update only the fields explicitly provided."""
    updates = payload.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(config, field, value)

    await db.commit()
    await db.refresh(config)

    return config


async def delete_assistant_config(
    db: AsyncSession,
    config: AssistantConfig,
) -> None:
    """Delete an assistant configuration."""
    await db.delete(config)
    await db.commit()
