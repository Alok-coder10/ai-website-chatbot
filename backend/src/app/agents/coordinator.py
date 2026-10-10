
from typing import Literal

from pydantic import BaseModel, Field

from app.agents.executor import (
    AgentExecutionResult,
    AgentExecutor,
)
from app.agents.schemas import AgentPlan, AgentStep


AgentRole = Literal["research", "compute", "python", "general"]


class CoordinatedTask(BaseModel):
    role: AgentRole
    step: AgentStep


class MultiAgentExecutionResult(BaseModel):
    goal: str
    assignments: list[CoordinatedTask] = Field(default_factory=list)
    execution: AgentExecutionResult
    success: bool


class MultiAgentCoordinator:
    """
    Routes planned tool steps to specialized agent roles and
    delegates all tool execution to AgentExecutor.
    """

    TOOL_ROLES: dict[str, AgentRole] = {
        "web_search": "research",
        "calculator": "compute",
        "python_execution": "python",
    }

    def __init__(self, executor: AgentExecutor):
        self.executor = executor

    def assign(self, plan: AgentPlan) -> list[CoordinatedTask]:
        if not isinstance(plan, AgentPlan):
            raise ValueError("Coordination requires an AgentPlan.")

        assignments = []

        for step in plan.steps:
            role = self.TOOL_ROLES.get(step.tool, "general")
            assignments.append(
                CoordinatedTask(role=role, step=step)
            )

        return assignments

    async def execute(
        self,
        plan: AgentPlan,
    ) -> MultiAgentExecutionResult:
        assignments = self.assign(plan)

        execution = await self.executor.execute(plan)

        return MultiAgentExecutionResult(
            goal=plan.goal,
            assignments=assignments,
            execution=execution,
            success=execution.success,
        )
