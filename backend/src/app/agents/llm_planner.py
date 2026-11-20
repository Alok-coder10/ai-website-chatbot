import json
from typing import Any

from pydantic import ValidationError

from app.agents.schemas import AgentPlan
from app.llm.factory import get_llm_provider


class LLMPlannerAgent:
    """
    Uses the application's LLM abstraction to convert a user
    request into a validated AgentPlan.
    """

    SYSTEM_PROMPT = """
You are an AI task planner.

Your job is to convert a user request into a structured execution plan.

Available tools:

1. calculator
   - Use for mathematical calculations.
   - Arguments:
     {"expression": "..."}

2. web_search
   - Use for current information or web searches.
   - Arguments:
     {"query": "..."}

3. python_execution
   - Use for Python calculations or data processing.
   - Arguments:
     {"code": "..."}

Return ONLY valid JSON.

Required format:

{
  "goal": "original user goal",
  "steps": [
    {
      "tool": "tool_name",
      "arguments": {}
    }
  ]
}

Rules:

- Only use the available tools.
- Do not invent tool names.
- Keep arguments inside the arguments object.
- Use an empty steps list when no tool is required.
- Do not include markdown.
- Do not include explanations outside the JSON.
"""

    def __init__(self):
        self.provider = get_llm_provider()

    async def plan(
        self,
        goal: str,
    ) -> AgentPlan:

        if not isinstance(goal, str):
            raise ValueError(
                "Goal must be a string."
            )

        goal = goal.strip()

        if not goal:
            raise ValueError(
                "Goal cannot be empty."
            )

        prompt = (
            f"{self.SYSTEM_PROMPT}\n\n"
            f"User request:\n{goal}"
        )

        response = await self.provider.generate(
            prompt
        )

        return self._parse_plan(
            response,
            goal,
        )

    def _parse_plan(
        self,
        response: str,
        original_goal: str,
    ) -> AgentPlan:

        if not isinstance(response, str):
            raise ValueError(
                "LLM planner response must be a string."
            )

        response = response.strip()

        if not response:
            raise ValueError(
                "LLM planner returned an empty response."
            )

        try:
            data: dict[str, Any] = json.loads(
                response
            )

        except json.JSONDecodeError as exc:
            raise ValueError(
                "LLM planner returned invalid JSON."
            ) from exc

        try:
            plan = AgentPlan.model_validate(
                data
            )

        except ValidationError as exc:
            raise ValueError(
                "LLM planner returned an invalid plan."
            ) from exc

        if not plan.goal:
            plan.goal = original_goal

        return plan