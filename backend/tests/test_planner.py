import pytest
from pydantic import ValidationError

from app.agents.planner import PlannerAgent
from app.agents.schemas import AgentPlan, AgentStep


@pytest.fixture
def planner():
    return PlannerAgent()


def test_calculator_plan(planner):

    plan = planner.plan(
        "Calculate 25 * 4"
    )

    assert isinstance(plan, AgentPlan)
    assert plan.goal == "Calculate 25 * 4"

    assert len(plan.steps) == 1

    step = plan.steps[0]

    assert isinstance(step, AgentStep)
    assert step.tool == "calculator"
    assert step.arguments["expression"] == "Calculate 25 * 4"


def test_web_search_plan(planner):

    plan = planner.plan(
        "Search the web for the latest AI news"
    )

    assert len(plan.steps) == 1

    step = plan.steps[0]

    assert step.tool == "web_search"
    assert (
        step.arguments["query"]
        == "Search the web for the latest AI news"
    )


def test_no_tool_plan(planner):

    plan = planner.plan(
        "Explain what artificial intelligence is"
    )

    assert plan.goal == (
        "Explain what artificial intelligence is"
    )

    assert plan.steps == []


def test_goal_is_trimmed(planner):

    plan = planner.plan(
        "   Calculate 2 + 2   "
    )

    assert plan.goal == "Calculate 2 + 2"


def test_empty_goal(planner):

    with pytest.raises(
        ValueError,
        match="Goal cannot be empty",
    ):
        planner.plan("   ")


def test_non_string_goal(planner):

    with pytest.raises(
        ValueError,
        match="Goal must be a string",
    ):
        planner.plan(123)


def test_agent_step_defaults_arguments():

    step = AgentStep(
        tool="calculator"
    )

    assert step.tool == "calculator"
    assert step.arguments == {}


def test_agent_plan_defaults_steps():

    plan = AgentPlan(
        goal="Test goal"
    )

    assert plan.steps == []


def test_invalid_agent_step():

    with pytest.raises(ValidationError):

        AgentStep(
            tool=123
        )


def test_invalid_agent_plan():

    with pytest.raises(ValidationError):

        AgentPlan(
            goal=123
        )