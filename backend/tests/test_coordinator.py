
import pytest

from app.agents.coordinator import MultiAgentCoordinator
from app.agents.executor import AgentExecutor
from app.agents.schemas import AgentPlan, AgentStep
from app.agents.tool import Tool
from app.agents.tool_registry import ToolRegistry
from app.agents.tool_router import ToolRouter


class FakeTool(Tool):
    def __init__(self, name, result):
        self.name = name
        self.description = f"Fake {name} tool"
        self.result = result

    async def execute(self, **kwargs):
        return {
            "result": self.result,
            "arguments": kwargs,
        }


def make_coordinator():
    registry = ToolRegistry()

    registry.register(FakeTool("web_search", "sources found"))
    registry.register(FakeTool("calculator", 42))
    registry.register(FakeTool("python_execution", "done"))

    executor = AgentExecutor(ToolRouter(registry))
    return MultiAgentCoordinator(executor)


def test_assigns_specialized_roles():
    coordinator = make_coordinator()

    plan = AgentPlan(
        goal="Research and calculate",
        steps=[
            AgentStep(
                tool="web_search",
                arguments={"query": "AI agents"},
            ),
            AgentStep(
                tool="calculator",
                arguments={"expression": "6 * 7"},
            ),
            AgentStep(
                tool="python_execution",
                arguments={"code": "print(42)"},
            ),
        ],
    )

    assignments = coordinator.assign(plan)

    assert [task.role for task in assignments] == [
        "research",
        "compute",
        "python",
    ]


def test_unknown_tool_gets_general_role():
    coordinator = make_coordinator()

    plan = AgentPlan(
        goal="Unknown tool",
        steps=[AgentStep(tool="unknown_tool")],
    )

    assignments = coordinator.assign(plan)

    assert assignments[0].role == "general"


@pytest.mark.asyncio
async def test_executes_coordinated_plan():
    coordinator = make_coordinator()

    plan = AgentPlan(
        goal="Research then calculate",
        steps=[
            AgentStep(
                tool="web_search",
                arguments={"query": "AI agents"},
            ),
            AgentStep(
                tool="calculator",
                arguments={"expression": "6 * 7"},
            ),
        ],
    )

    result = await coordinator.execute(plan)

    assert result.success is True
    assert result.goal == plan.goal
    assert len(result.assignments) == 2
    assert len(result.execution.steps) == 2
    assert result.execution.steps[1].success is True


@pytest.mark.asyncio
async def test_propagates_execution_failure():
    coordinator = make_coordinator()

    plan = AgentPlan(
        goal="Test missing tool",
        steps=[AgentStep(tool="missing_tool")],
    )

    result = await coordinator.execute(plan)

    assert result.success is False
    assert result.execution.success is False


@pytest.mark.asyncio
async def test_empty_plan_succeeds():
    coordinator = make_coordinator()

    plan = AgentPlan(goal="No work", steps=[])

    result = await coordinator.execute(plan)

    assert result.success is True
    assert result.assignments == []
    assert result.execution.steps == []
