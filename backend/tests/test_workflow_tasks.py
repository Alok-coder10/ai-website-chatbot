from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.agents.task_queue import TaskQueue
from app.agents.workflow_tasks import WorkflowTaskService


@pytest.mark.asyncio
async def test_submit_workflow_task():
    queue = TaskQueue()
    runner = AsyncMock()
    service = WorkflowTaskService(queue, runner)

    task = await service.submit("Summarize a document")

    assert task.task_type == "agent_workflow"
    assert task.payload == {"goal": "Summarize a document"}
    assert task.status == "pending"
    runner.run.assert_not_awaited()



@pytest.mark.asyncio
async def test_process_workflow_task():
    queue = TaskQueue()
    runner = AsyncMock()

    workflow_result = MagicMock()
    workflow_result.model_dump.return_value = {
        "goal": "Test workflow",
        "memory_saved": False,
    }
    runner.run.return_value = workflow_result

    service = WorkflowTaskService(queue, runner)

    submitted = await service.submit("Test workflow")
    processed = await service.process_next()

    assert processed is not None
    assert processed.id == submitted.id
    assert processed.status == "completed"
    assert processed.result["goal"] == "Test workflow"
    runner.run.assert_awaited_once_with("Test workflow")



@pytest.mark.asyncio
async def test_get_status_for_unknown_task():
    service = WorkflowTaskService(TaskQueue(), AsyncMock())

    assert await service.get_status(uuid4()) is None


@pytest.mark.asyncio
async def test_empty_queue_returns_none():
    service = WorkflowTaskService(TaskQueue(), AsyncMock())

    assert await service.process_next() is None


@pytest.mark.asyncio
async def test_submit_rejects_empty_goal():
    service = WorkflowTaskService(TaskQueue(), AsyncMock())

    with pytest.raises(ValueError, match="goal"):
        await service.submit("   ")
