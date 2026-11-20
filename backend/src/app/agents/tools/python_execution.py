import ast
import asyncio
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

from app.agents.tool import Tool


class PythonExecutionTool(Tool):

    name = "python_execution"

    description = (
        "Executes a restricted Python program and returns its "
        "standard output and execution status."
    )

    DEFAULT_TIMEOUT = 5
    MAX_TIMEOUT = 10
    MAX_OUTPUT_SIZE = 10_000
    MAX_CODE_SIZE = 20_000

    BLOCKED_NODES = (
        ast.Import,
        ast.ImportFrom,
    )

    BLOCKED_CALLS = {
        "eval",
        "exec",
        "compile",
        "__import__",
        "open",
        "input",
        "breakpoint",
    }

    BLOCKED_NAMES = {
        "__builtins__",
        "__globals__",
        "__locals__",
        "__import__",
        "__loader__",
        "__spec__",
        "__file__",
        "__cached__",
    }

    async def execute(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:

        code = kwargs.get("code")

        if not isinstance(code, str):
            raise ValueError(
                "Python execution requires a 'code' string."
            )

        code = code.strip()

        if not code:
            raise ValueError(
                "Python code cannot be empty."
            )

        if len(code) > self.MAX_CODE_SIZE:
            raise ValueError(
                "Python code exceeds the maximum allowed size."
            )

        timeout = kwargs.get(
            "timeout",
            self.DEFAULT_TIMEOUT,
        )

        if not isinstance(timeout, (int, float)):
            raise ValueError(
                "Timeout must be a number."
            )

        if timeout <= 0:
            raise ValueError(
                "Timeout must be greater than zero."
            )

        timeout = min(
            timeout,
            self.MAX_TIMEOUT,
        )

        self._validate_code(code)

        with tempfile.TemporaryDirectory(
            prefix="nyaya_python_"
        ) as temp_dir:

            script_path = Path(temp_dir) / "main.py"
            script_path.write_text(
                code,
                encoding="utf-8",
            )

            environment = {
                "PATH": os.environ.get(
                    "PATH",
                    "",
                ),
                "PYTHONIOENCODING": "utf-8",
            }

            process = await asyncio.create_subprocess_exec(
                sys.executable,
                "-I",
                str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=temp_dir,
                env=environment,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout,
                )

            except asyncio.TimeoutError:

                process.kill()

                await process.communicate()

                raise RuntimeError(
                    f"Python execution timed out after "
                    f"{timeout} seconds."
                )

        stdout_text = stdout.decode(
            "utf-8",
            errors="replace",
        ).replace("\r\n", "\n")

        stderr_text = stderr.decode(
            "utf-8",
            errors="replace",
        ).replace("\r\n", "\n")

        if len(stdout_text) > self.MAX_OUTPUT_SIZE:
            stdout_text = (
                stdout_text[:self.MAX_OUTPUT_SIZE]
                + "\n[output truncated]"
            )

        if len(stderr_text) > self.MAX_OUTPUT_SIZE:
            stderr_text = (
                stderr_text[:self.MAX_OUTPUT_SIZE]
                + "\n[error output truncated]"
            )

        if process.returncode != 0:
            return {
                "status": "error",
                "stdout": stdout_text,
                "stderr": stderr_text,
                "return_code": process.returncode,
            }

        return {
            "status": "success",
            "stdout": stdout_text,
            "stderr": stderr_text,
            "return_code": 0,
        }

    def _validate_code(
        self,
        code: str,
    ) -> None:

        try:
            tree = ast.parse(
                code,
                mode="exec",
            )

        except SyntaxError as exc:
            raise ValueError(
                "Invalid Python syntax."
            ) from exc

        for node in ast.walk(tree):

            if isinstance(
                node,
                self.BLOCKED_NODES,
            ):
                raise ValueError(
                    "Import statements are not allowed."
                )

            if isinstance(node, ast.Name):
                if node.id in self.BLOCKED_NAMES:
                    raise ValueError(
                        f"Access to '{node.id}' is not allowed."
                    )

            if isinstance(node, ast.Call):

                if isinstance(
                    node.func,
                    ast.Name,
                ):
                    if node.func.id in self.BLOCKED_CALLS:
                        raise ValueError(
                            f"Call to '{node.func.id}' "
                            "is not allowed."
                        )