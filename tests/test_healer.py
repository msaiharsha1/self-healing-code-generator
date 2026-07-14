"""Tests for the healer module."""

from unittest.mock import Mock, patch

import pytest

from src.healer import CodeHealer, generate_validated_code
from src.models import CodeGenerationResponse, ValidationResult


class TestCodeHealer:
    """Test the CodeHealer class."""

    def test_initialization(self):
        with patch("src.healer.get_llm_provider") as mock_get_provider:
            mock_provider = Mock()
            mock_get_provider.return_value = mock_provider

            healer = CodeHealer(llm_provider="openai", max_retries=3)

            assert healer.max_retries == 3
            assert healer.llm_provider == mock_provider

    def test_successful_generation_first_try(self):
        with (
            patch("src.healer.get_llm_provider") as mock_get_provider,
            patch("src.healer.validate_ast") as mock_validate_ast,
            patch("src.healer.validate_runtime") as mock_validate_runtime,
        ):
            mock_llm = Mock()
            mock_llm.generate.return_value = "def add(a, b):\n    return a + b"
            mock_get_provider.return_value = mock_llm

            mock_validate_ast.return_value = ValidationResult(success=True)
            mock_validate_runtime.return_value = ValidationResult(success=True)

            healer = CodeHealer(max_retries=3)
            response = healer.generate_and_fix("Write a function to add two numbers")

            assert response.status == "success"
            assert response.attempts == 1
            assert response.validated is True
            assert "def add" in response.code

    def test_repair_on_syntax_error(self):
        with (
            patch("src.healer.get_llm_provider") as mock_get_provider,
            patch("src.healer.validate_ast") as mock_validate_ast,
            patch("src.healer.validate_runtime") as mock_validate_runtime,
        ):
            mock_llm = Mock()
            mock_llm.generate.side_effect = [
                "def add(a, b)\n    return a + b",
                "def add(a, b):\n    return a + b",
            ]
            mock_get_provider.return_value = mock_llm

            mock_validate_ast.side_effect = [
                ValidationResult(
                    success=False,
                    error_type="SyntaxError",
                    error_message="Invalid syntax",
                ),
                ValidationResult(success=True),
            ]
            mock_validate_runtime.return_value = ValidationResult(success=True)

            healer = CodeHealer(max_retries=3)
            response = healer.generate_and_fix("Write a function to add two numbers")

            assert response.status == "success"
            assert response.attempts == 2
            assert mock_llm.generate.call_count == 2

    def test_repair_on_runtime_error(self):
        with (
            patch("src.healer.get_llm_provider") as mock_get_provider,
            patch("src.healer.validate_ast") as mock_validate_ast,
            patch("src.healer.validate_runtime") as mock_validate_runtime,
        ):
            mock_llm = Mock()
            mock_llm.generate.side_effect = [
                "result = 10 / 0\nprint(result)",
                "result = 10 / 2\nprint(result)",
            ]
            mock_get_provider.return_value = mock_llm

            mock_validate_ast.return_value = ValidationResult(success=True)
            mock_validate_runtime.side_effect = [
                ValidationResult(
                    success=False,
                    error_type="ZeroDivisionError",
                    error_message="division by zero",
                ),
                ValidationResult(success=True),
            ]

            healer = CodeHealer(max_retries=3)
            response = healer.generate_and_fix("Write code that divides 10 by 2")

            assert response.status == "success"
            assert response.attempts == 2

    def test_max_retries_exceeded(self):
        with (
            patch("src.healer.get_llm_provider") as mock_get_provider,
            patch("src.healer.validate_ast") as mock_validate_ast,
        ):
            mock_llm = Mock()
            mock_llm.generate.return_value = "def broken("
            mock_get_provider.return_value = mock_llm

            mock_validate_ast.return_value = ValidationResult(
                success=False,
                error_type="SyntaxError",
                error_message="Invalid syntax",
            )

            healer = CodeHealer(max_retries=3)

            with pytest.raises(RuntimeError, match="Failed to generate valid code"):
                healer.generate_and_fix("Write a function")


class TestGenerateValidatedCode:
    """Test the async wrapper function."""

    @pytest.mark.asyncio
    async def test_async_wrapper(self):
        with patch("src.healer.CodeHealer") as MockHealer:
            mock_healer_instance = Mock()
            mock_healer_instance.generate_and_fix.return_value = CodeGenerationResponse(
                status="success",
                attempts=1,
                validated=True,
                code="print('hello')",
                execution_time=0.5,
            )
            MockHealer.return_value = mock_healer_instance

            response = await generate_validated_code("Write hello world")

            assert response.status == "success"
            MockHealer.assert_called_once()
            mock_healer_instance.generate_and_fix.assert_called_once()
