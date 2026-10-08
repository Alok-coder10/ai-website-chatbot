import pytest

from app.agents.tools.calculator import CalculatorTool


@pytest.fixture
def calculator():
    return CalculatorTool()


@pytest.mark.asyncio
async def test_basic_arithmetic(calculator):

    result = await calculator.execute(
        expression="2 + 3"
    )

    assert result["status"] == "success"
    assert result["expression"] == "2 + 3"
    assert result["result"] == 5


@pytest.mark.asyncio
async def test_operator_precedence(calculator):

    result = await calculator.execute(
        expression="2 + 3 * 4"
    )

    assert result["result"] == 14


@pytest.mark.asyncio
async def test_parentheses(calculator):

    result = await calculator.execute(
        expression="(2 + 3) * 4"
    )

    assert result["result"] == 20


@pytest.mark.asyncio
async def test_decimals(calculator):

    result = await calculator.execute(
        expression="2.5 * 4"
    )

    assert result["result"] == 10.0


@pytest.mark.asyncio
async def test_negative_numbers(calculator):

    result = await calculator.execute(
        expression="-5 + 10"
    )

    assert result["result"] == 5


@pytest.mark.asyncio
async def test_power(calculator):

    result = await calculator.execute(
        expression="2 ** 5"
    )

    assert result["result"] == 32


@pytest.mark.asyncio
async def test_modulo(calculator):

    result = await calculator.execute(
        expression="10 % 3"
    )

    assert result["result"] == 1


@pytest.mark.asyncio
async def test_division(calculator):

    result = await calculator.execute(
        expression="20 / 4"
    )

    assert result["result"] == 5


@pytest.mark.asyncio
async def test_division_by_zero(calculator):

    with pytest.raises(
        ValueError,
        match="Division by zero"
    ):
        await calculator.execute(
            expression="10 / 0"
        )


@pytest.mark.asyncio
async def test_empty_expression(calculator):

    with pytest.raises(
        ValueError,
        match="Expression cannot be empty"
    ):
        await calculator.execute(
            expression=""
        )


@pytest.mark.asyncio
async def test_invalid_expression(calculator):

    with pytest.raises(
        ValueError,
        match="Invalid or unsupported"
    ):
        await calculator.execute(
            expression="2 +"
        )


@pytest.mark.asyncio
async def test_unsupported_function(calculator):

    with pytest.raises(
        ValueError,
        match="Invalid or unsupported"
    ):
        await calculator.execute(
            expression="sqrt(16)"
        )


@pytest.mark.asyncio
async def test_arbitrary_code_execution_is_blocked(calculator):

    with pytest.raises(ValueError):
        await calculator.execute(
            expression='__import__("os").system("whoami")'
        )


@pytest.mark.asyncio
async def test_open_file_is_blocked(calculator):

    with pytest.raises(ValueError):
        await calculator.execute(
            expression='open("secret.txt")'
        )


@pytest.mark.asyncio
async def test_eval_is_blocked(calculator):

    with pytest.raises(ValueError):
        await calculator.execute(
            expression='eval("2 + 2")'
        )


@pytest.mark.asyncio
async def test_non_string_expression_is_rejected(calculator):

    with pytest.raises(
        ValueError,
        match="expression.*string"
    ):
        await calculator.execute(
            expression=123
        )