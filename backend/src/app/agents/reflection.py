
from typing import Literal

from pydantic import BaseModel, Field

from app.agents.executor import AgentExecutionResult


ReflectionStatus = Literal[
    "accepted",
    "needs_retry",
    "failed",
]


class ReflectionResult(BaseModel):
    status: ReflectionStatus
    accepted: bool
    retry_recommended: bool
    issues: list[str] = Field(default_factory=list)
    summary: str


class ReflectionAgent:
    """
    Deterministically evaluates agent execution results.

    This first version checks execution status and tool errors.
    It does not claim to verify the factual correctness of results.
    """

    def reflect(
        self,
        execution: AgentExecutionResult,
    ) -> ReflectionResult:

        if not isinstance(execution, AgentExecutionResult):
            raise ValueError(
                "Reflection requires an AgentExecutionResult."
            )

        issues: list[str] = []

        for index, step in enumerate(execution.steps, start=1):
            if not step.success:
                issues.append(
                    f"Step {index} using tool '{step.tool}' failed: "
                    f"{step.error or 'Unknown error'}"
                )

        if not execution.success or issues:
            return ReflectionResult(
                status="needs_retry",
                accepted=False,
                retry_recommended=True,
                issues=issues or [
                    "Execution reported failure without a step-level error."
                ],
                summary=(
                    "Execution was unsuccessful. Review the failed steps "
                    "before deciding whether to retry."
                ),
            )

        return ReflectionResult(
            status="accepted",
            accepted=True,
            retry_recommended=False,
            issues=[],
            summary=(
                "All planned steps completed successfully. "
                "Factual correctness has not been independently verified."
            ),
        )
