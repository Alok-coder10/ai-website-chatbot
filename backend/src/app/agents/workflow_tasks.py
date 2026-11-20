
from typing import Any
from uuid import UUID

from app.agents.task_queue import TaskQueue, TaskRecord
from app.agents.workflow import AgentWorkflowRunner


WORKFLOW_TASK_TYPE = "agent_workflow"


class WorkflowTaskService:
    """Submits agent workflows to the existing in-process task queue."""

    def __init__(
        self,
        queue: TaskQueue,
        runner: AgentWorkflowRunner,
    ):
        self.queue = queue
        self.runner = runner

    async def submit(self, goal: str) -> TaskRecord:
        if not isinstance(goal, str) or not goal.strip():
            raise ValueError("Workflow goal cannot be empty.")

        return await self.queue.submit(
            task_type=WORKFLOW_TASK_TYPE,
            payload={"goal": goal.strip()},
        )

    async def get_status(self, task_id: UUID) -> TaskRecord | None:
        return await self.queue.get(task_id)

    def handlers(self) -> dict[str, Any]:
        async def run_workflow(payload: dict[str, Any]) -> dict[str, Any]:
            goal = payload.get("goal")

            if not isinstance(goal, str) or not goal.strip():
                raise ValueError("Workflow task requires a non-empty goal.")

            result = await self.runner.run(goal)
            return result.model_dump(mode="json")

        return {WORKFLOW_TASK_TYPE: run_workflow}

    async def process_next(self) -> TaskRecord | None:
        return await self.queue.process_next(self.handlers())
