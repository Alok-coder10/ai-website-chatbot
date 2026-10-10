import asyncio
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AgentMemoryRecord(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    agent_id: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class AgentMemoryStore:
    """
    In-memory store for agent-specific observations and outcomes.

    This store is not persistent: memories are lost on process restart.
    """

    def __init__(self):
        self._memories: dict[str, list[AgentMemoryRecord]] = {}
        self._lock = asyncio.Lock()

    async def save(
        self,
        agent_id: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> AgentMemoryRecord:
        if not isinstance(agent_id, str) or not agent_id.strip():
            raise ValueError("Agent ID cannot be empty.")

        if not isinstance(content, str) or not content.strip():
            raise ValueError("Memory content cannot be empty.")

        if metadata is not None and not isinstance(metadata, dict):
            raise ValueError("Memory metadata must be a dictionary.")

        record = AgentMemoryRecord(
            agent_id=agent_id.strip(),
            content=content.strip(),
            metadata=metadata or {},
        )

        async with self._lock:
            self._memories.setdefault(record.agent_id, []).append(record)

        return record.model_copy(deep=True)

    async def get(
        self,
        memory_id: UUID,
    ) -> AgentMemoryRecord | None:
        async with self._lock:
            for records in self._memories.values():
                for record in records:
                    if record.id == memory_id:
                        return record.model_copy(deep=True)

        return None

    async def list_memories(
        self,
        agent_id: str,
        *,
        limit: int = 100,
    ) -> list[AgentMemoryRecord]:
        if not isinstance(agent_id, str) or not agent_id.strip():
            raise ValueError("Agent ID cannot be empty.")

        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("Limit must be a positive integer.")

        async with self._lock:
            records = self._memories.get(agent_id.strip(), [])
            selected = records[-limit:]

            return [
                record.model_copy(deep=True)
                for record in reversed(selected)
            ]

    async def search(
        self,
        agent_id: str,
        query: str,
        *,
        limit: int = 10,
    ) -> list[AgentMemoryRecord]:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Search query cannot be empty.")

        query_terms = set(query.casefold().split())

        records = await self.list_memories(
            agent_id,
            limit=10000,
        )

        matches = [
            record
            for record in records
            if query_terms.intersection(
                set(record.content.casefold().split())
            )
        ]

        return matches[:limit]

    async def delete(
        self,
        memory_id: UUID,
    ) -> bool:
        async with self._lock:
            for agent_id, records in self._memories.items():
                for index, record in enumerate(records):
                    if record.id == memory_id:
                        del records[index]
                        if not records:
                            del self._memories[agent_id]
                        return True

        return False

    async def clear_agent(self, agent_id: str) -> int:
        if not isinstance(agent_id, str) or not agent_id.strip():
            raise ValueError("Agent ID cannot be empty.")

        async with self._lock:
            records = self._memories.pop(agent_id.strip(), [])
            return len(records)
