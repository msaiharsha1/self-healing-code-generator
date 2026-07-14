"""Code validation module using AST parsing and sandboxed runtime execution."""

import ast

from src.logger import logger
from src.models import ValidationResult
from src.sandbox import execute_in_sandbox


def validate_ast(code: str) -> ValidationResult:
    """Validate Python code syntax using AST parsing."""
    try:
        ast.parse(code)
        return ValidationResult(success=True)
    except SyntaxError as e:
        error_msg = f"SyntaxError: {e.msg} at line {e.lineno}, column {e.offset}"
        logger.warning(f"AST validation failed: {error_msg}")
        return ValidationResult(
            success=False,
            error_type="SyntaxError",
            error_message=error_msg,
        )
    except Exception as e:
        error_msg = f"Unexpected AST error: {type(e).__name__}: {e}"
        logger.error(error_msg)
        return ValidationResult(
            success=False,
            error_type=type(e).__name__,
            error_message=error_msg,
        )


def validate_runtime(code: str, test_input: str = "") -> ValidationResult:
    """Execute Python code in an isolated subprocess and capture results."""
    try:
        result = execute_in_sandbox(code, test_input=test_input)

        if result["success"]:
            return ValidationResult(
                success=True,
                stdout=result["stdout"].strip() or None,
                stderr=result["stderr"].strip() or None,
            )

        logger.warning(
            f"Runtime validation failed: {result['error_type']} - {result['error_message']}"
        )
        return ValidationResult(
            success=False,
            error_type=result.get("error_type", "ExecutionError"),
            error_message=result.get("error_message", "Unknown execution error"),
            stdout=result["stdout"].strip() or None,
            stderr=result["stderr"].strip() or None,
            traceback=result.get("traceback"),
        )

    except Exception as e:
        error_msg = f"Unexpected validation error: {type(e).__name__}: {e}"
        logger.error(error_msg)
        return ValidationResult(
            success=False,
            error_type=type(e).__name__,
            error_message=error_msg,
        )


def validate_complete(code: str, test_input: str = "") -> ValidationResult:
    """Perform both AST and runtime validation."""
    syntax_result = validate_ast(code)
    if not syntax_result.success:
        return syntax_result
    return validate_runtime(code, test_input)
