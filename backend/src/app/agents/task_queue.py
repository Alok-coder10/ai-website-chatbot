
import asyncio
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


TaskStatus = Literal[
    "pending",
    "running",
    "completed",
    "failed",
]

TaskHandler = Callable[
    [dict[str, Any]],
    Awaitable[Any],
]


class TaskRecord(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    task_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    status: TaskStatus = "pending"
    result: Any = None
    error: str | None = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    started_at: datetime | None = None
    completed_at: datetime | None = None


class TaskQueue:
    """
    In-process asynchronous task queue.

    Tasks are held in memory and will be lost when the process
    restarts. Persistent storage and distributed workers are
    separate future additions.
    """

    def __init__(self):
        self._queue: asyncio.Queue[UUID] = asyncio.Queue()
        self._tasks: dict[UUID, TaskRecord] = {}
        self._lock = asyncio.Lock()

    async def submit(
        self,
        task_type: str,
        payload: dict[str, Any] | None = None,
    ) -> TaskRecord:
        if not isinstance(task_type, str) or not task_type.strip():
            raise ValueError("Task type cannot be empty.")

        if payload is not None and not isinstance(payload, dict):
            raise ValueError("Task payload must be a dictionary.")

        task = TaskRecord(
            task_type=task_type.strip(),
            payload=payload or {},
        )

        async with self._lock:
            self._tasks[task.id] = task
            await self._queue.put(task.id)

        return task.model_copy(deep=True)

    async def get(self, task_id: UUID) -> TaskRecord | None:
        async with self._lock:
            task = self._tasks.get(task_id)
            return task.model_copy(deep=True) if task else None

    async def process_next(
        self,
        handlers: dict[str, TaskHandler],
    ) -> TaskRecord | None:
        """
        Process one queued task using its registered handler.
        Returns None if the queue is empty.
        """
        try:
            task_id = self._queue.get_nowait()
        except asyncio.QueueEmpty:
            return None

        try:
            async with self._lock:
                task = self._tasks[task_id]
                task.status = "running"
                task.started_at = datetime.now(timezone.utc)
                task.error = None

                task_type = task.task_type
                payload = task.payload.copy()

            handler = handlers.get(task_type)

            if handler is None:
                raise ValueError(
                    f"No handler registered for task type: {task_type}"
                )

            result = await handler(payload)

            async with self._lock:
                task = self._tasks[task_id]
                task.result = result
                task.status = "completed"
                task.completed_at = datetime.now(timezone.utc)

        except Exception as exc:
            async with self._lock:
                task = self._tasks[task_id]
                task.status = "failed"
                task.error = str(exc)
                task.completed_at = datetime.now(timezone.utc)

        finally:
            self._queue.task_done()

        async with self._lock:
            return self._tasks[task_id].model_copy(deep=True)

    async def pending_count(self) -> int:
        return self._queue.qsize()
