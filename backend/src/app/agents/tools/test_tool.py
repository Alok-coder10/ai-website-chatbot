from app.agents.tool import Tool


class TestTool(Tool):

    name = "test"
    description = "A simple test tool."

    async def execute(self, **kwargs):
        return {
            "status": "success",
            "message": "Tool executed successfully",
            "arguments": kwargs,
        }