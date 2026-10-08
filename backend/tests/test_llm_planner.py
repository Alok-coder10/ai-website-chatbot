import pytest

from app.agents.llm_planner import LLMPlannerAgent


class FakeLLMProvider:

    def __init__(self, response):
        self.response = response
        self.last_prompt = None

    async def generate(self, prompt: str) -> str:
        self.last_prompt = prompt
        return self.response


@pytest.mark.asyncio
async def test_llm_planner_returns_valid_plan(
    monkeypatch,
):

    provider = FakeLLMProvider(
        """
        {
            "goal": "Calculate 25 * 4",
            "steps": [
                {
                    "tool": "calculator",
                    "arguments": {
                        "expression": "25 * 4"
                    }
                }
            ]
        }
        """
    )

    monkeypatch.setattr(
        "app.agents.llm_planner.get_llm_provider",
        lambda: provider,
    )

    planner = LLMPlannerAgent()

    plan = await planner.plan(
        "Calculate 25 * 4"
    )

    assert plan.goal == "Calculate 25 * 4"
    assert len(plan.steps) == 1

    assert plan.steps[0].tool == "calculator"
    assert (
        plan.steps[0].arguments["expression"]
        == "25 * 4"
    )


@pytest.mark.asyncio
async def test_llm_planner_web_search(
    monkeypatch,
):

    provider = FakeLLMProvider(
        """
        {
            "goal": "Find the latest AI news",
            "steps": [
                {
                    "tool": "web_search",
                    "arguments": {
                        "query": "latest AI news"
                    }
                }
            ]
        }
        """
    )

    monkeypatch.setattr(
        "app.agents.llm_planner.get_llm_provider",
        lambda: provider,
    )

    planner = LLMPlannerAgent()

    plan = await planner.plan(
        "Find the latest AI news"
    )

    assert len(plan.steps) == 1
    assert plan.steps[0].tool == "web_search"


@pytest.mark.asyncio
async def test_llm_planner_multi_step_plan(
    monkeypatch,
):

    provider = FakeLLMProvider(
        """
        {
            "goal": "Search for a number and calculate something",
            "steps": [
                {
                    "tool": "web_search",
                    "arguments": {
                        "query": "population of India"
                    }
                },
                {
                    "tool": "calculator",
                    "arguments": {
                        "expression": "100 + 50"
                    }
                }
            ]
        }
        """
    )

    monkeypatch.setattr(
        "app.agents.llm_planner.get_llm_provider",
        lambda: provider,
    )

    planner = LLMPlannerAgent()

    plan = await planner.plan(
        "Search for a number and calculate something"
    )

    assert len(plan.steps) == 2

    assert plan.steps[0].tool == "web_search"
    assert plan.steps[1].tool == "calculator"


@pytest.mark.asyncio
async def test_empty_goal(
    monkeypatch,
):

    provider = FakeLLMProvider("{}")

    monkeypatch.setattr(
        "app.agents.llm_planner.get_llm_provider",
        lambda: provider,
    )

    planner = LLMPlannerAgent()

    with pytest.raises(
        ValueError,
        match="Goal cannot be empty",
    ):
        await planner.plan("   ")


@pytest.mark.asyncio
async def test_non_string_goal(
    monkeypatch,
):

    provider = FakeLLMProvider("{}")

    monkeypatch.setattr(
        "app.agents.llm_planner.get_llm_provider",
        lambda: provider,
    )

    planner = LLMPlannerAgent()

    with pytest.raises(
        ValueError,
        match="Goal must be a string",
    ):
        await planner.plan(123)


def test_invalid_json():

    planner = object.__new__(
        LLMPlannerAgent
    )

    with pytest.raises(
        ValueError,
        match="invalid JSON",
    ):
        planner._parse_plan(
            "this is not json",
            "test",
        )


def test_invalid_plan():

    planner = object.__new__(
        LLMPlannerAgent
    )

    with pytest.raises(
        ValueError,
        match="invalid plan",
    ):
        planner._parse_plan(
            """
            {
                "goal": "test",
                "steps": [
                    {
                        "arguments": {}
                    }
                ]
            }
            """,
            "test",
        )


def test_empty_llm_response():

    planner = object.__new__(
        LLMPlannerAgent
    )

    with pytest.raises(
        ValueError,
        match="empty response",
    ):
        planner._parse_plan(
            "",
            "test",
        )