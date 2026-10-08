import pytest

from app.agents.tool_registry import ToolRegistry
from app.agents.tool_router import ToolRouter
from app.agents.tools.test_tool import TestTool


@pytest.mark.asyncio
async def test_tool_registration_and_execution():

    registry = ToolRegistry()

    tool = TestTool()
    registry.register(tool)

    assert registry.has("test")
    assert registry.get("test") is tool

    router = ToolRouter(registry)

    result = await router.execute(
        "test",
        value="hello"
    )

    assert result["status"] == "success"
    assert result["message"] == "Tool executed successfully"
    assert result["arguments"]["value"] == "hello"

@pytest.mark.asyncio
async def test_unknown_tool():

    registry = ToolRegistry()
    router = ToolRouter(registry)

    with pytest.raises(ValueError, match="Unknown tool"):
        await router.execute("does_not_exist")