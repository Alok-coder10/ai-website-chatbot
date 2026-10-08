import pytest

from app.agents.executor import AgentExecutor
from app.agents.schemas import AgentPlan, AgentStep
from app.agents.tool import Tool
from app.agents.tool_registry import ToolRegistry
from app.agents.tool_router import ToolRouter


class EchoTool(Tool):

    name = "echo"
    description = "Returns the supplied value."

    async def execute(self, **kwargs):
        return {
            "value": kwargs.get("value")
        }


class AddTool(Tool):

    name = "add"
    description = "Adds two numbers."

    async def execute(self, **kwargs):
        return (
            kwargs["a"] + kwargs["b"]
        )


class FailingTool(Tool):

    name = "failing"
    description = "Always fails."

    async def execute(self, **kwargs):
        raise RuntimeError(
            "Tool execution failed"
        )


def create_executor(*tools: Tool) -> AgentExecutor:

    registry = ToolRegistry()

    for tool in tools:
        registry.register(tool)

    router = ToolRouter(registry)

    return AgentExecutor(router)


@pytest.mark.asyncio
async def test_execute_single_step():

    executor = create_executor(
        EchoTool()
    )

    plan = AgentPlan(
        goal="Echo hello",
        steps=[
            AgentStep(
                tool="echo",
                arguments={
                    "value": "hello"
                },
            )
        ],
    )

    result = await executor.execute(plan)

    assert result.success is True
    assert result.goal == "Echo hello"

    assert len(result.steps) == 1

    step = result.steps[0]

    assert step.tool == "echo"
    assert step.success is True
    assert step.result == {
        "value": "hello"
    }


@pytest.mark.asyncio
async def test_execute_multiple_steps_sequentially():

    executor = create_executor(
        EchoTool(),
        AddTool(),
    )

    plan = AgentPlan(
        goal="Run multiple tools",
        steps=[
            AgentStep(
                tool="echo",
                arguments={
                    "value": "first"
                },
            ),
            AgentStep(
                tool="add",
                arguments={
                    "a": 10,
                    "b": 20,
                },
            ),
        ],
    )

    result = await executor.execute(plan)

    assert result.success is True
    assert len(result.steps) == 2

    assert result.steps[0].result == {
        "value": "first"
    }

    assert result.steps[1].result == 30


@pytest.mark.asyncio
async def test_execute_empty_plan():

    executor = create_executor()

    plan = AgentPlan(
        goal="Nothing to execute",
        steps=[],
    )

    result = await executor.execute(plan)

    assert result.success is True
    assert result.goal == "Nothing to execute"
    assert result.steps == []


@pytest.mark.asyncio
async def test_execution_stops_after_failure():

    executor = create_executor(
        EchoTool(),
        FailingTool(),
        AddTool(),
    )

    plan = AgentPlan(
        goal="Test failure handling",
        steps=[
            AgentStep(
                tool="echo",
                arguments={
                    "value": "before"
                },
            ),
            AgentStep(
                tool="failing",
            ),
            AgentStep(
                tool="add",
                arguments={
                    "a": 10,
                    "b": 20,
                },
            ),
        ],
    )

    result = await executor.execute(plan)

    assert result.success is False

    assert len(result.steps) == 2

    assert result.steps[0].success is True
    assert result.steps[1].success is False

    assert result.steps[1].tool == "failing"

    assert (
        result.steps[1].error
        == "Tool execution failed"
    )


@pytest.mark.asyncio
async def test_unknown_tool_is_handled():

    executor = create_executor()

    plan = AgentPlan(
        goal="Unknown tool test",
        steps=[
            AgentStep(
                tool="does_not_exist",
            )
        ],
    )

    result = await executor.execute(plan)

    assert result.success is False
    assert len(result.steps) == 1

    assert result.steps[0].success is False
    assert result.steps[0].tool == "does_not_exist"

    assert (
        result.steps[0].error
        == "Unknown tool: does_not_exist"
    )


@pytest.mark.asyncio
async def test_non_agent_plan_is_rejected():

    executor = create_executor()

    with pytest.raises(
        ValueError,
        match="AgentPlan",
    ):
        await executor.execute(
            "not a plan"
        )