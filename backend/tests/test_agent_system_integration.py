
import asyncio
from unittest.mock import AsyncMock

import pytest

from app.agents.task_queue import TaskQueue
from app.agents.workflow_tasks import WorkflowTaskService
from app.agents.worker import AgentWorker


@pytest.mark.asyncio
async def test_worker_processes_workflow_task_end_to_end():
    queue = TaskQueue()
    runner = AsyncMock()

    workflow_result = AsyncMock()
    workflow_result.model_dump.return_value = {
        "goal": "Calculate 2 + 3",
        "memory_saved": True,
        "attempt_count": 1,
    }
    runner.run.return_value = workflow_result

    workflow_service = WorkflowTaskService(
        queue=queue,
        runner=runner,
    )

    worker = AgentWorker(
        queue=queue,
        handlers=workflow_service.handlers(),
    )

    submitted = await workflow_service.submit("Calculate 2 + 3")

    assert submitted.status == "pending"

    processed = await worker.run_once()

    assert processed is True

    task = await workflow_service.get_status(submitted.id)

    assert task is not None
    assert task.status == "completed"
    assert task.result["goal"] == "Calculate 2 + 3"
    assert task.result["memory_saved"] is True

    runner.run.assert_awaited_once_with("Calculate 2 + 3")


@pytest.mark.asyncio
async def test_worker_records_workflow_failure():
    queue = TaskQueue()
    runner = AsyncMock()
    runner.run.side_effect = RuntimeError("Workflow failed")

    workflow_service = WorkflowTaskService(queue, runner)

    worker = AgentWorker(
        queue=queue,
        handlers=workflow_service.handlers(),
    )

    submitted = await workflow_service.submit("Run a failing workflow")
    await worker.run_once()

    task = await workflow_service.get_status(submitted.id)

    assert task is not None
    assert task.status == "failed"
    assert "Workflow failed" in task.error


@pytest.mark.asyncio
async def test_worker_processes_multiple_tasks_in_order():
    queue = TaskQueue()
    completed = []

    async def handler(payload):
        await asyncio.sleep(0)
        completed.append(payload["number"])
        return {"number": payload["number"]}

    await queue.submit("number", {"number": 1})
    await queue.submit("number", {"number": 2})
    await queue.submit("number", {"number": 3})

    worker = AgentWorker(queue, {"number": handler})

    assert await worker.run_once() is True
    assert await worker.run_once() is True
    assert await worker.run_once() is True
    assert await worker.run_once() is False

    assert completed == [1, 2, 3]
    assert await queue.pending_count() == 0
