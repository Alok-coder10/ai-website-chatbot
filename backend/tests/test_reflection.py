
import pytest

from app.agents.executor import (
    AgentExecutionResult,
    AgentStepResult,
)
from app.agents.reflection import ReflectionAgent


def test_accepts_successful_execution():
    agent = ReflectionAgent()

    execution = AgentExecutionResult(
        goal="Calculate a value",
        success=True,
        steps=[
            AgentStepResult(
                tool="calculator",
                arguments={"expression": "6 * 7"},
                result={"result": 42},
                success=True,
            )
        ],
    )

    result = agent.reflect(execution)

    assert result.status == "accepted"
    assert result.accepted is True
    assert result.retry_recommended is False
    assert result.issues == []


def test_recommends_retry_after_step_failure():
    agent = ReflectionAgent()

    execution = AgentExecutionResult(
        goal="Search the web",
        success=False,
        steps=[
            AgentStepResult(
                tool="web_search",
                arguments={"query": "AI agents"},
                success=False,
                error="Service unavailable",
            )
        ],
    )

    result = agent.reflect(execution)

    assert result.status == "needs_retry"
    assert result.accepted is False
    assert result.retry_recommended is True
    assert len(result.issues) == 1
    assert "Service unavailable" in result.issues[0]


def test_detects_failure_in_multi_step_execution():
    agent = ReflectionAgent()

    execution = AgentExecutionResult(
        goal="Research and calculate",
        success=False,
        steps=[
            AgentStepResult(
                tool="web_search",
                result={"results": ["source"]},
                success=True,
            ),
            AgentStepResult(
                tool="calculator",
                success=False,
                error="Division by zero",
            ),
        ],
    )

    result = agent.reflect(execution)

    assert result.accepted is False
    assert result.retry_recommended is True
    assert len(result.issues) == 1
    assert "calculator" in result.issues[0]


def test_detects_top_level_failure_without_step_errors():
    agent = ReflectionAgent()

    execution = AgentExecutionResult(
        goal="Unknown failure",
        success=False,
        steps=[],
    )

    result = agent.reflect(execution)

    assert result.status == "needs_retry"
    assert result.retry_recommended is True
    assert len(result.issues) == 1


def test_accepts_empty_successful_execution():
    agent = ReflectionAgent()

    execution = AgentExecutionResult(
        goal="No work required",
        success=True,
        steps=[],
    )

    result = agent.reflect(execution)

    assert result.status == "accepted"
    assert result.accepted is True


def test_rejects_invalid_input():
    agent = ReflectionAgent()

    with pytest.raises(
        ValueError,
        match="AgentExecutionResult",
    ):
        agent.reflect("invalid")
