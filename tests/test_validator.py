"""Tests for the validator module."""

from src.validator import validate_ast, validate_complete, validate_runtime


class TestValidateAST:
    """Test AST validation functionality."""

    def test_valid_function(self):
        code = "def add(a, b):\n    return a + b\n"
        result = validate_ast(code)
        assert result.success is True
        assert result.error_type is None

    def test_valid_class(self):
        code = (
            "class Calculator:\n"
            "    def __init__(self):\n"
            "        self.value = 0\n"
            "    def add(self, x):\n"
            "        self.value += x\n"
            "        return self.value\n"
        )
        result = validate_ast(code)
        assert result.success is True

    def test_syntax_error_missing_colon(self):
        code = "def add(a, b)\n    return a + b\n"
        result = validate_ast(code)
        assert result.success is False
        assert result.error_type == "SyntaxError"

    def test_syntax_error_indentation(self):
        code = "def add(a, b):\nreturn a + b\n"
        result = validate_ast(code)
        assert result.success is False
        assert result.error_type == "SyntaxError"

    def test_syntax_error_unclosed_paren(self):
        code = "result = (1 + 2\n"
        result = validate_ast(code)
        assert result.success is False
        assert result.error_type == "SyntaxError"


class TestValidateRuntime:
    """Test runtime validation functionality."""

    def test_simple_print(self):
        result = validate_runtime('print("Hello, World!")')
        assert result.success is True
        assert "Hello, World!" in (result.stdout or "")

    def test_function_definition_and_call(self):
        code = (
            "def greet(name):\n"
            '    return f"Hello, {name}!"\n'
            'print(greet("Alice"))\n'
        )
        result = validate_runtime(code)
        assert result.success is True
        assert "Hello, Alice!" in (result.stdout or "")

    def test_runtime_error_division_by_zero(self):
        result = validate_runtime("result = 10 / 0\nprint(result)")
        assert result.success is False
        assert result.error_type == "ZeroDivisionError"

    def test_runtime_error_name_error(self):
        result = validate_runtime("print(undefined_variable)")
        assert result.success is False
        assert result.error_type == "NameError"

    def test_list_operations(self):
        code = (
            "numbers = [1, 2, 3, 4, 5]\n"
            "squared = [x ** 2 for x in numbers]\n"
            "print(sum(squared))\n"
        )
        result = validate_runtime(code)
        assert result.success is True
        assert "55" in (result.stdout or "")


class TestValidateComplete:
    """Test complete validation (AST + runtime)."""

    def test_valid_code_complete(self):
        code = (
            "def multiply(a, b):\n"
            "    return a * b\n"
            "result = multiply(5, 3)\n"
            'print(f"Result: {result}")\n'
        )
        result = validate_complete(code)
        assert result.success is True

    def test_syntax_error_stops_validation(self):
        code = 'def broken_function(\n    print("This will not run")\n'
        result = validate_complete(code)
        assert result.success is False
        assert result.error_type == "SyntaxError"
