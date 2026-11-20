from typing import Any

from pydantic import BaseModel, Field

from app.agents.schemas import AgentPlan
from app.agents.tool_router import ToolRouter


class AgentStepResult(BaseModel):
    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    result: Any = None
    success: bool = True
    error: str | None = None


class AgentExecutionResult(BaseModel):
    goal: str
    steps: list[AgentStepResult] = Field(default_factory=list)
    success: bool = True


class AgentExecutor:
    """
    Executes an AgentPlan sequentially through the ToolRouter.

    The executor never calls tools directly. All tool execution
    goes through ToolRouter.
    """

    def __init__(self, router: ToolRouter):
        self.router = router

    async def execute(
        self,
        plan: AgentPlan,
    ) -> AgentExecutionResult:

        if not isinstance(plan, AgentPlan):
            raise ValueError(
                "Execution requires an AgentPlan."
            )

        step_results: list[AgentStepResult] = []

        for step in plan.steps:

            try:
                result = await self.router.execute(
                    step.tool,
                    **step.arguments,
                )

                step_results.append(
                    AgentStepResult(
                        tool=step.tool,
                        arguments=step.arguments,
                        result=result,
                        success=True,
                    )
                )

            except Exception as exc:

                step_results.append(
                    AgentStepResult(
                        tool=step.tool,
                        arguments=step.arguments,
                        result=None,
                        success=False,
                        error=str(exc),
                    )
                )

                return AgentExecutionResult(
                    goal=plan.goal,
                    steps=step_results,
                    success=False,
                )

        return AgentExecutionResult(
            goal=plan.goal,
            steps=step_results,
            success=True,
        )