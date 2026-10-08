from typing import Any
from app.agents.tool_registry import ToolRegistry

class ToolRouter:

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    async def execute(
        self,
        tool_name: str,
        **kwargs: Any
    ) -> Any:

        tool = self.registry.get(tool_name)

        if tool is None:
            raise ValueError(
                f"Unknown tool: {tool_name}"
            )

        return await tool.execute(**kwargs)