
from typing import Any

from pydantic import BaseModel, Field

from app.agents.executor import AgentExecutor, AgentExecutionResult
from app.agents.planner import PlannerAgent
from app.agents.reflection import ReflectionAgent, ReflectionResult
from app.agents.schemas import AgentPlan


class WorkflowAttempt(BaseModel):
    attempt_number: int
    plan: AgentPlan
    execution: AgentExecutionResult
    reflection: ReflectionResult


class WorkflowResult(BaseModel):
    goal: str
    plan: AgentPlan
    execution: AgentExecutionResult
    reflection: ReflectionResult
    memory_saved: bool = False
    errors: list[str] = Field(default_factory=list)
    attempts: list[WorkflowAttempt] = Field(default_factory=list)

    @property
    def attempt_count(self) -> int:
        return len(self.attempts)


class AgentWorkflowRunner:
    """Coordinates planning, execution, reflection, and bounded retries."""

    def __init__(
        self,
        planner: PlannerAgent,
        executor: AgentExecutor,
        reflector: ReflectionAgent,
        memory: Any | None = None,
        agent_id: str = "workflow",
        max_attempts: int = 3,
    ):
        if (
            isinstance(max_attempts, bool)
            or not isinstance(max_attempts, int)
            or max_attempts < 1
        ):
            raise ValueError("max_attempts must be a positive integer.")

        if not isinstance(agent_id, str) or not agent_id.strip():
            raise ValueError("Agent ID cannot be empty.")

        self.planner = planner
        self.executor = executor
        self.reflector = reflector
        self.memory = memory
        self.agent_id = agent_id.strip()
        self.max_attempts = max_attempts

    async def run(self, goal: str) -> WorkflowResult:
        if not isinstance(goal, str) or not goal.strip():
            raise ValueError("Workflow goal cannot be empty.")

        goal = goal.strip()
        errors: list[str] = []
        attempts: list[WorkflowAttempt] = []

        plan: AgentPlan | None = None
        execution: AgentExecutionResult | None = None
        reflection: ReflectionResult | None = None

        for attempt_number in range(1, self.max_attempts + 1):
            plan = await self.planner.plan(goal)
            execution = await self.executor.execute(plan)
            reflection = await self.reflector.reflect(execution)

            attempts.append(
                WorkflowAttempt(
                    attempt_number=attempt_number,
                    plan=plan,
                    execution=execution,
                    reflection=reflection,
                )
            )

            if reflection.accepted:
                break

            if not reflection.retry_recommended:
                break

            if attempt_number == self.max_attempts:
                errors.append(
                    f"Retry limit reached after {self.max_attempts} attempts."
                )
                break

        # The loop always executes at least once because max_attempts >= 1.
        assert plan is not None
        assert execution is not None
        assert reflection is not None

        memory_saved = False

        if self.memory is not None and reflection.accepted:
            try:
                await self.memory.save(
                    agent_id=self.agent_id,
                    content=(
                        f"Goal: {goal}\n"
                        f"Result: {execution.model_dump_json()}"
                    ),
                    metadata={
                        "status": reflection.status,
                        "summary": reflection.summary,
                        "attempt_count": len(attempts),
                    },
                )
                memory_saved = True
            except Exception as exc:
                errors.append(f"Memory save failed: {exc}")

        return WorkflowResult(
            goal=goal,
            plan=plan,
            execution=execution,
            reflection=reflection,
            memory_saved=memory_saved,
            errors=errors,
            attempts=attempts,
        )
