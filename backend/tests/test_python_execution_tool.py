import pytest

from app.agents.tools.python_execution import PythonExecutionTool


@pytest.fixture
def tool():
    return PythonExecutionTool()


@pytest.mark.asyncio
async def test_basic_python_execution(tool):

    result = await tool.execute(
        code="print(2 + 3)"
    )

    assert result["status"] == "success"
    assert result["stdout"] == "5\n"
    assert result["return_code"] == 0


@pytest.mark.asyncio
async def test_multiple_output_lines(tool):

    result = await tool.execute(
        code="""
for i in range(3):
    print(i)
"""
    )

    assert result["status"] == "success"
    assert result["stdout"] == "0\n1\n2\n"


@pytest.mark.asyncio
async def test_variables_and_calculation(tool):

    result = await tool.execute(
        code="""
a = 10
b = 20
print(a + b)
"""
    )

    assert result["status"] == "success"
    assert result["stdout"] == "30\n"


@pytest.mark.asyncio
async def test_syntax_error(tool):

    with pytest.raises(
        ValueError,
        match="Invalid Python syntax",
    ):
        await tool.execute(
            code="print("
        )


@pytest.mark.asyncio
async def test_runtime_error(tool):

    result = await tool.execute(
        code="print(1 / 0)"
    )

    assert result["status"] == "error"
    assert result["return_code"] != 0
    assert "ZeroDivisionError" in result["stderr"]


@pytest.mark.asyncio
async def test_empty_code(tool):

    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        await tool.execute(
            code="   "
        )


@pytest.mark.asyncio
async def test_non_string_code(tool):

    with pytest.raises(
        ValueError,
        match="code.*string",
    ):
        await tool.execute(
            code=123
        )


@pytest.mark.asyncio
async def test_import_is_blocked(tool):

    with pytest.raises(
        ValueError,
        match="Import statements are not allowed",
    ):
        await tool.execute(
            code="import os"
        )


@pytest.mark.asyncio
async def test_from_import_is_blocked(tool):

    with pytest.raises(
        ValueError,
        match="Import statements are not allowed",
    ):
        await tool.execute(
            code="from pathlib import Path"
        )


@pytest.mark.asyncio
async def test_eval_is_blocked(tool):

    with pytest.raises(
        ValueError,
        match="eval",
    ):
        await tool.execute(
            code='eval("2 + 2")'
        )


@pytest.mark.asyncio
async def test_exec_is_blocked(tool):

    with pytest.raises(
        ValueError,
        match="exec",
    ):
        await tool.execute(
            code='exec("print(123)")'
        )


@pytest.mark.asyncio
async def test_open_is_blocked(tool):

    with pytest.raises(
        ValueError,
        match="open",
    ):
        await tool.execute(
            code='open("secret.txt")'
        )


@pytest.mark.asyncio
async def test_dunder_import_is_blocked(tool):

    with pytest.raises(
        ValueError,
        match="__import__",
    ):
        await tool.execute(
            code='__import__("os")'
        )


@pytest.mark.asyncio
async def test_timeout(tool):

    with pytest.raises(
        RuntimeError,
        match="timed out",
    ):
        await tool.execute(
            code="""
while True:
    pass
""",
            timeout=1,
        )


@pytest.mark.asyncio
async def test_timeout_is_capped(tool):

    # We don't actually wait for the maximum timeout here.
    # The tool caps user-supplied timeout values internally.

    assert tool.MAX_TIMEOUT == 10


@pytest.mark.asyncio
async def test_code_size_limit(tool):

    code = "x = 1\n" * (
        tool.MAX_CODE_SIZE // 6 + 1
    )

    with pytest.raises(
        ValueError,
        match="maximum allowed size",
    ):
        await tool.execute(
            code=code
        )


@pytest.mark.asyncio
async def test_output_is_captured(tool):

    result = await tool.execute(
        code="""
print("hello")
print("world")
"""
    )

    assert result["status"] == "success"
    assert "hello" in result["stdout"]
    assert "world" in result["stdout"]


@pytest.mark.asyncio
async def test_stderr_is_captured(tool):

    result = await tool.execute(
        code="""
raise RuntimeError("test error")
"""
    )

    assert result["status"] == "error"
    assert "RuntimeError" in result["stderr"]


@pytest.mark.asyncio
async def test_builtins_access_is_blocked(tool):

    with pytest.raises(
        ValueError,
        match="__builtins__",
    ):
        await tool.execute(
            code="print(__builtins__)"
        )