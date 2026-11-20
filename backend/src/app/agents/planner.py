from app.agents.schemas import AgentPlan, AgentStep


class PlannerAgent:
    """
    Deterministic planner used as the foundation for the
    future LLM-backed planner.
    """

    def plan(self, goal: str) -> AgentPlan:

        if not isinstance(goal, str):
            raise ValueError(
                "Goal must be a string."
            )

        goal = goal.strip()

        if not goal:
            raise ValueError(
                "Goal cannot be empty."
            )

        normalized = goal.lower()

        # Explicit arithmetic requests.
        arithmetic_keywords = (
            "calculate",
            "compute",
            "solve",
            "what is",
        )

        if any(
            keyword in normalized
            for keyword in arithmetic_keywords
        ):
            return AgentPlan(
                goal=goal,
                steps=[
                    AgentStep(
                        tool="calculator",
                        arguments={
                            "expression": goal,
                        },
                    )
                ],
            )

        # Explicit web-search requests.
        search_keywords = (
            "search",
            "look up",
            "find online",
            "latest",
            "current",
            "news",
        )

        if any(
            keyword in normalized
            for keyword in search_keywords
        ):
            return AgentPlan(
                goal=goal,
                steps=[
                    AgentStep(
                        tool="web_search",
                        arguments={
                            "query": goal,
                        },
                    )
                ],
            )

        # Default: no tool required yet.
        return AgentPlan(
            goal=goal,
            steps=[],
        )