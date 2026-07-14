"""Secure code execution sandbox using subprocess isolation."""

import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from src.config import settings
from src.logger import logger

_ERROR_LINE_RE = re.compile(r"^(\w+(?:\.\w+)*(?:Error|Exception|Interrupt|Exit|Warning)):?\s*(.*)$")


def _parse_error(stderr: str) -> tuple[str | None, str | None]:
    """Extract the error type and message from a Python traceback."""
    for line in reversed(stderr.strip().splitlines()):
        match = _ERROR_LINE_RE.match(line.strip())
        if match:
            return match.group(1), match.group(2) or match.group(1)
    return "ExecutionError", stderr.strip() or "Unknown execution error"


def execute_in_sandbox(
    code: str,
    test_input: str = "",
    timeout: int | None = None,
) -> dict[str, Any]:
    """
    Execute Python code in an isolated subprocess with a timeout.

    Returns a dict with success status, stdout, stderr, and error details.
    """
    if timeout is None:
        timeout = settings.execution_timeout

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as f:
        f.write(code)
        temp_file = f.name

    try:
        result = subprocess.run(
            [sys.executable, "-I", temp_file],
            input=test_input,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=tempfile.gettempdir(),
        )

        if result.returncode == 0:
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "error_type": None,
                "error_message": None,
                "traceback": None,
                "returncode": 0,
            }

        error_type, error_message = _parse_error(result.stderr)
        return {
            "success": False,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "error_type": error_type,
            "error_message": error_message,
            "traceback": result.stderr.strip() or None,
            "returncode": result.returncode,
        }

    except subprocess.TimeoutExpired:
        logger.warning(f"Code execution timed out after {timeout} seconds")
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Execution timed out after {timeout} seconds",
            "error_type": "TimeoutError",
            "error_message": f"Execution timed out after {timeout} seconds",
            "traceback": None,
            "returncode": -1,
        }

    except Exception as e:
        logger.error(f"Sandbox execution error: {type(e).__name__}: {e}")
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": None,
            "returncode": -1,
        }

    finally:
        try:
            Path(temp_file).unlink()
        except OSError:
            pass
