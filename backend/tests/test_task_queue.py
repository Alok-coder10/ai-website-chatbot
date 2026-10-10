
import pytest

from app.agents.task_queue import TaskQueue


@pytest.mark.asyncio
async def test_submit_creates_pending_task():
    queue = TaskQueue()

    task = await queue.submit(
        "calculate",
        {"expression": "6 * 7"},
    )

    assert task.task_type == "calculate"
    assert task.payload == {"expression": "6 * 7"}
    assert task.status == "pending"
    assert task.id is not None
    assert await queue.pending_count() == 1


@pytest.mark.asyncio
async def test_get_returns_task():
    queue = TaskQueue()
    task = await queue.submit("demo", {"value": 10})

    retrieved = await queue.get(task.id)

    assert retrieved is not None
    assert retrieved.id == task.id
    assert retrieved.status == "pending"


@pytest.mark.asyncio
async def test_successful_task_execution():
    queue = TaskQueue()

    async def calculate(payload):
        return {"result": 6 * 7}

    await queue.submit("calculate", {})

    result = await queue.process_next(
        {"calculate": calculate}
    )

    assert result is not None
    assert result.status == "completed"
    assert result.result == {"result": 42}
    assert result.error is None
    assert result.started_at is not None
    assert result.completed_at is not None
    assert await queue.pending_count() == 0


@pytest.mark.asyncio
async def test_failed_task_execution():
    queue = TaskQueue()

    async def failing_handler(payload):
        raise RuntimeError("Execution failed")

    await queue.submit("failing", {})

    result = await queue.process_next(
        {"failing": failing_handler}
    )

    assert result is not None
    assert result.status == "failed"
    assert result.error == "Execution failed"
    assert result.completed_at is not None


@pytest.mark.asyncio
async def test_missing_handler_marks_task_failed():
    queue = TaskQueue()
    await queue.submit("unknown", {})

    result = await queue.process_next({})

    assert result is not None
    assert result.status == "failed"
    assert "No handler registered" in result.error


@pytest.mark.asyncio
async def test_empty_queue_returns_none():
    queue = TaskQueue()

    assert await queue.process_next({}) is None


@pytest.mark.asyncio
async def test_tasks_are_processed_in_order():
    queue = TaskQueue()
    executed = []

    async def handler(payload):
        executed.append(payload["number"])
        return payload["number"]

    first = await queue.submit("demo", {"number": 1})
    second = await queue.submit("demo", {"number": 2})

    result1 = await queue.process_next({"demo": handler})
    result2 = await queue.process_next({"demo": handler})

    assert result1.id == first.id
    assert result2.id == second.id
    assert executed == [1, 2]


@pytest.mark.asyncio
async def test_invalid_task_type_is_rejected():
    queue = TaskQueue()

    with pytest.raises(ValueError, match="Task type"):
        await queue.submit("   ")


@pytest.mark.asyncio
async def test_unknown_task_id_returns_none():
    from uuid import uuid4

    queue = TaskQueue()

    assert await queue.get(uuid4()) is None
