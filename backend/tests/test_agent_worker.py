
import asyncio

import pytest

from app.agents.task_queue import TaskQueue
from app.agents.worker import AgentWorker


@pytest.mark.asyncio
async def test_worker_processes_queued_task():
    queue = TaskQueue()
    results = []

    async def handler(payload):
        results.append(payload["value"])
        return {"processed": True}

    await queue.submit("example", {"value": 42})

    worker = AgentWorker(
        queue=queue,
        handlers={"example": handler},
    )

    processed = await worker.run_once()

    assert processed is True
    assert results == [42]
    assert await queue.pending_count() == 0


@pytest.mark.asyncio
async def test_worker_returns_false_when_queue_is_empty():
    worker = AgentWorker(TaskQueue(), {})

    assert await worker.run_once() is False


@pytest.mark.asyncio
async def test_worker_stop_exits_run_loop():
    worker = AgentWorker(
        TaskQueue(),
        {},
        poll_interval=0.01,
    )

    worker_task = asyncio.create_task(worker.run())
    await asyncio.sleep(0.03)
    worker.stop()

    await asyncio.wait_for(worker_task, timeout=1)


def test_worker_rejects_invalid_poll_interval():
    with pytest.raises(ValueError, match="poll_interval"):
        AgentWorker(TaskQueue(), {}, poll_interval=0)
