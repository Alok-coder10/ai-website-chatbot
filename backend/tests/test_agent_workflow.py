
from unittest.mock import AsyncMock

import pytest

from app.agents.executor import AgentExecutionResult
from app.agents.reflection import ReflectionResult
from app.agents.schemas import AgentPlan
from app.agents.workflow import AgentWorkflowRunner


@pytest.fixture
def plan():
    return AgentPlan(
        goal="Calculate 2 + 3",
        steps=[],
    )


@pytest.fixture
def execution():
    return AgentExecutionResult(
        goal="Calculate 2 + 3",
        success=True,
        steps=[],
    )


@pytest.fixture
def accepted_reflection():
    return ReflectionResult(
        status="accepted",
        accepted=True,
        retry_recommended=False,
        issues=[],
        summary="Execution succeeded.",
    )


@pytest.mark.asyncio
async def test_workflow_runs_planner_executor_and_reflector(
    plan,
    execution,
    accepted_reflection,
):
    planner = AsyncMock()
    planner.plan.return_value = plan

    executor = AsyncMock()
    executor.execute.return_value = execution

    reflector = AsyncMock()
    reflector.reflect.return_value = accepted_reflection

    runner = AgentWorkflowRunner(
        planner=planner,
        executor=executor,
        reflector=reflector,
    )

    result = await runner.run("Calculate 2 + 3")

    assert result.goal == "Calculate 2 + 3"
    assert result.plan == plan
    assert result.execution == execution
    assert result.reflection == accepted_reflection

    planner.plan.assert_awaited_once_with("Calculate 2 + 3")
    executor.execute.assert_awaited_once_with(plan)
    reflector.reflect.assert_awaited_once_with(execution)


@pytest.mark.asyncio
async def test_workflow_saves_accepted_result_to_memory(
    plan,
    execution,
    accepted_reflection,
):
    planner = AsyncMock()
    planner.plan.return_value = plan

    executor = AsyncMock()
    executor.execute.return_value = execution

    reflector = AsyncMock()
    reflector.reflect.return_value = accepted_reflection

    memory = AsyncMock()

    runner = AgentWorkflowRunner(
        planner=planner,
        executor=executor,
        reflector=reflector,
        memory=memory,
        agent_id="research",
    )

    result = await runner.run("Calculate 2 + 3")

    assert result.memory_saved is True
    memory.save.assert_awaited_once()

    saved_kwargs = memory.save.await_args.kwargs
    assert saved_kwargs["agent_id"] == "research"
    assert "Calculate 2 + 3" in saved_kwargs["content"]


@pytest.mark.asyncio
async def test_workflow_does_not_save_rejected_result(
    plan,
    execution,
):
    planner = AsyncMock()
    planner.plan.return_value = plan

    executor = AsyncMock()
    executor.execute.return_value = execution

    reflection = ReflectionResult(
        status="needs_retry",
        accepted=False,
        retry_recommended=True,
        issues=["Execution needs another attempt."],
        summary="Review required.",
    )

    reflector = AsyncMock()
    reflector.reflect.return_value = reflection

    memory = AsyncMock()

    runner = AgentWorkflowRunner(
        planner=planner,
        executor=executor,
        reflector=reflector,
        memory=memory,
    )

    result = await runner.run("Calculate 2 + 3")

    assert result.memory_saved is False
    memory.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_workflow_handles_memory_save_failure(
    plan,
    execution,
    accepted_reflection,
):
    planner = AsyncMock()
    planner.plan.return_value = plan

    executor = AsyncMock()
    executor.execute.return_value = execution

    reflector = AsyncMock()
    reflector.reflect.return_value = accepted_reflection

    memory = AsyncMock()
    memory.save.side_effect = RuntimeError("Storage unavailable")

    runner = AgentWorkflowRunner(
        planner=planner,
        executor=executor,
        reflector=reflector,
        memory=memory,
    )

    result = await runner.run("Calculate 2 + 3")

    assert result.memory_saved is False
    assert len(result.errors) == 1
    assert "Memory save failed" in result.errors[0]


@pytest.mark.asyncio
async def test_workflow_rejects_empty_goal():
    runner = AgentWorkflowRunner(
        planner=AsyncMock(),
        executor=AsyncMock(),
        reflector=AsyncMock(),
    )

    with pytest.raises(ValueError, match="goal"):
        await runner.run("   ")


@pytest.mark.asyncio
async def test_workflow_retries_then_succeeds(
    plan,
    execution,
    accepted_reflection,
):
    planner = AsyncMock()
    planner.plan.return_value = plan

    executor = AsyncMock()
    executor.execute.return_value = execution

    needs_retry = ReflectionResult(
        status="needs_retry",
        accepted=False,
        retry_recommended=True,
        issues=["First attempt needs review."],
        summary="Retry recommended.",
    )

    reflector = AsyncMock()
    reflector.reflect.side_effect = [
        needs_retry,
        accepted_reflection,
    ]

    runner = AgentWorkflowRunner(
        planner=planner,
        executor=executor,
        reflector=reflector,
        max_attempts=3,
    )

    result = await runner.run("Calculate 2 + 3")

    assert result.reflection.accepted is True
    assert result.attempt_count == 2
    assert [a.attempt_number for a in result.attempts] == [1, 2]
    assert planner.plan.await_count == 2
    assert executor.execute.await_count == 2
    assert reflector.reflect.await_count == 2
    assert result.errors == []


@pytest.mark.asyncio
async def test_workflow_stops_after_retry_limit(
    plan,
    execution,
):
    planner = AsyncMock()
    planner.plan.return_value = plan

    executor = AsyncMock()
    executor.execute.return_value = execution

    needs_retry = ReflectionResult(
        status="needs_retry",
        accepted=False,
        retry_recommended=True,
        issues=["Result needs review."],
        summary="Retry recommended.",
    )

    reflector = AsyncMock()
    reflector.reflect.return_value = needs_retry

    runner = AgentWorkflowRunner(
        planner=planner,
        executor=executor,
        reflector=reflector,
        max_attempts=2,
    )

    result = await runner.run("Calculate 2 + 3")

    assert result.attempt_count == 2
    assert result.reflection.retry_recommended is True
    assert planner.plan.await_count == 2
    assert executor.execute.await_count == 2
    assert any("Retry limit reached" in e for e in result.errors)


@pytest.mark.asyncio
async def test_workflow_does_not_retry_when_not_recommended(
    plan,
    execution,
):
    planner = AsyncMock()
    planner.plan.return_value = plan

    executor = AsyncMock()
    executor.execute.return_value = execution

    rejected = ReflectionResult(
        status="failed",
        accepted=False,
        retry_recommended=False,
        issues=["Cannot recover from this failure."],
        summary="Workflow stopped.",
    )

    reflector = AsyncMock()
    reflector.reflect.return_value = rejected

    runner = AgentWorkflowRunner(
        planner=planner,
        executor=executor,
        reflector=reflector,
        max_attempts=3,
    )

    result = await runner.run("Calculate 2 + 3")

    assert result.attempt_count == 1
    assert result.reflection.status == "failed"
    planner.plan.assert_awaited_once()
    executor.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_workflow_rejects_invalid_max_attempts():
    for invalid_value in (0, -1, True):
        with pytest.raises(ValueError, match="max_attempts"):
            AgentWorkflowRunner(
                planner=AsyncMock(),
                executor=AsyncMock(),
                reflector=AsyncMock(),
                max_attempts=invalid_value,
            )
