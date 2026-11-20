from typing import Any

from pydantic import BaseModel, Field


class AgentStep(BaseModel):
    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class AgentPlan(BaseModel):
    goal: str
    steps: list[AgentStep] = Field(default_factory=list)