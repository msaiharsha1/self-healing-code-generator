"""Self-healing code generation module implementing the validate-repair loop."""

import time

from src.config import settings
from src.llm import get_llm_provider
from src.logger import logger
from src.models import (
    CodeGenerationResponse,
    GenerationHistory,
    RepairAttempt,
)
from src.prompts import SYSTEM_PROMPT, get_initial_prompt, get_repair_prompt
from src.validator import validate_ast, validate_runtime


class CodeHealer:
    """Self-healing code generator that validates and repairs AI-generated code."""

    def __init__(
        self,
        llm_provider: str | None = None,
        max_retries: int | None = None,
    ):
        self.llm_provider = get_llm_provider(llm_provider)
        self.max_retries = max_retries or settings.max_retries
        self.history = GenerationHistory(prompt="")

    def generate_and_fix(self, prompt: str, test_input: str = "") -> CodeGenerationResponse:
        """
        Generate code and automatically repair validation errors.

        Raises:
            RuntimeError: If maximum retries are exceeded without valid code.
        """
        start_time = time.time()
        self.history = GenerationHistory(prompt=prompt)

        current_prompt = get_initial_prompt(prompt)

        for attempt in range(1, self.max_retries + 1):
            logger.info(f"Repair attempt {attempt}/{self.max_retries}")

            attempt_record = RepairAttempt(
                attempt_number=attempt,
                code="",
                syntax_valid=False,
            )

            try:
                code = self.llm_provider.generate(
                    prompt=current_prompt,
                    system_prompt=SYSTEM_PROMPT,
                )
                attempt_record.code = code

                # Syntax validation
                syntax_result = validate_ast(code)
                attempt_record.syntax_valid = syntax_result.success

                if not syntax_result.success:
                    error_info = f"Syntax Error: {syntax_result.error_message}"
                    current_prompt = get_repair_prompt(prompt, code, error_info)
                    attempt_record.error = syntax_result.error_message
                    self.history.attempts.append(attempt_record)
                    continue

                # Runtime validation
                runtime_result = validate_runtime(code, test_input)
                attempt_record.runtime_valid = runtime_result.success

                if not runtime_result.success:
                    error_parts = []
                    if runtime_result.error_type:
                        error_parts.append(f"Error Type: {runtime_result.error_type}")
                    if runtime_result.error_message:
                        error_parts.append(f"Error Message: {runtime_result.error_message}")
                    if runtime_result.traceback:
                        error_parts.append(f"Traceback:\n{runtime_result.traceback}")

                    current_prompt = get_repair_prompt(prompt, code, "\n".join(error_parts))
                    attempt_record.error = runtime_result.error_message
                    self.history.attempts.append(attempt_record)
                    continue

                # Code passed all validations
                logger.info(f"Code validated successfully after {attempt} attempts")
                self.history.final_code = code
                self.history.success = True
                self.history.total_time = time.time() - start_time

                return CodeGenerationResponse(
                    status="success",
                    attempts=attempt,
                    validated=True,
                    code=code,
                    execution_time=self.history.total_time,
                )

            except Exception as e:
                logger.error(f"Attempt {attempt} failed with exception: {e}")
                attempt_record.error = str(e)
                self.history.attempts.append(attempt_record)
                if attempt == self.max_retries:
                    raise

        logger.error(f"Maximum retries ({self.max_retries}) exceeded")
        self.history.total_time = time.time() - start_time
        last_error = self.history.attempts[-1].error if self.history.attempts else "Unknown"

        raise RuntimeError(
            f"Failed to generate valid code after {self.max_retries} attempts. "
            f"Last error: {last_error}"
        )

    def get_history(self) -> GenerationHistory:
        """Return the generation history."""
        return self.history


async def generate_validated_code(
    prompt: str,
    llm_provider: str | None = None,
    max_retries: int | None = None,
    test_input: str = "",
) -> CodeGenerationResponse:
    """Async wrapper for code generation with self-healing."""
    healer = CodeHealer(llm_provider=llm_provider, max_retries=max_retries)
    return healer.generate_and_fix(prompt, test_input)
