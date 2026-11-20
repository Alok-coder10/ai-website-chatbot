import ast
import operator
from typing import Any

from app.agents.tool import Tool


class CalculatorTool(Tool):

    name = "calculator"
    description = (
        "Safely evaluates basic mathematical expressions including "
        "addition, subtraction, multiplication, division, modulo, "
        "exponentiation, and parentheses."
    )

    _operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    async def execute(self, **kwargs: Any) -> dict[str, Any]:

        expression = kwargs.get("expression")

        if not isinstance(expression, str):
            raise ValueError(
                "Calculator requires an 'expression' string."
            )

        expression = expression.strip()

        if not expression:
            raise ValueError(
                "Expression cannot be empty."
            )

        try:
            tree = ast.parse(
                expression,
                mode="eval"
            )

            result = self._evaluate(tree.body)

        except ZeroDivisionError:
            raise ValueError(
                "Division by zero is not allowed."
            )

        except (SyntaxError, ValueError, TypeError, OverflowError):
            raise ValueError(
                "Invalid or unsupported mathematical expression."
            )

        return {
            "status": "success",
            "expression": expression,
            "result": result,
        }

    def _evaluate(self, node: ast.AST) -> int | float:

        if isinstance(node, ast.Constant):

            if isinstance(node.value, bool):
                raise ValueError(
                    "Boolean values are not allowed."
                )

            if isinstance(node.value, (int, float)):
                return node.value

            raise ValueError(
                "Only numeric constants are allowed."
            )

        if isinstance(node, ast.BinOp):

            operation = self._operators.get(
                type(node.op)
            )

            if operation is None:
                raise ValueError(
                    "Unsupported operator."
                )

            left = self._evaluate(node.left)
            right = self._evaluate(node.right)

            if isinstance(node.op, ast.Pow):

                if abs(right) > 100:
                    raise ValueError(
                        "Exponent is too large."
                    )

                if abs(left) > 10**6:
                    raise ValueError(
                        "Base is too large."
                    )

            return operation(left, right)

        if isinstance(node, ast.UnaryOp):

            operation = self._operators.get(
                type(node.op)
            )

            if operation is None:
                raise ValueError(
                    "Unsupported unary operator."
                )

            operand = self._evaluate(node.operand)

            return operation(operand)

        raise ValueError(
            "Unsupported expression."
        )