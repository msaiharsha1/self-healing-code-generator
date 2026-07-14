"""Prompt templates for LLM interactions."""

SYSTEM_PROMPT = """You are an expert Python engineer specializing in writing clean, efficient, and correct Python code.

CRITICAL INSTRUCTIONS:
- Return ONLY executable Python code with no explanations
- Never use markdown formatting (no ```python or ``` blocks)
- The code must be complete and runnable as-is
- Import all necessary modules at the top
- Handle edge cases appropriately

If you receive error information about previous code:
- Carefully analyze the provided error message or traceback
- Fix the specific issues mentioned
- Do not change working parts unnecessarily
- Return the complete corrected code
"""

REPAIR_PROMPT_TEMPLATE = """I need you to repair Python code that failed validation.

ORIGINAL PROMPT:
{original_prompt}

PREVIOUS CODE THAT FAILED:
```python
{previous_code}
```

ERROR INFORMATION:
{error_info}

Please fix the issues and return ONLY the corrected Python code.
Do not include any explanations, markdown, or comments.
"""

INITIAL_GENERATION_PROMPT_TEMPLATE = """Write Python code for the following task:

{prompt}

Return ONLY the Python code. No explanations. No markdown.
"""


def get_initial_prompt(prompt: str) -> str:
    """Generate the initial prompt for code generation."""
    return INITIAL_GENERATION_PROMPT_TEMPLATE.format(prompt=prompt)


def get_repair_prompt(original_prompt: str, previous_code: str, error_info: str) -> str:
    """Generate a repair prompt with error context."""
    return REPAIR_PROMPT_TEMPLATE.format(
        original_prompt=original_prompt,
        previous_code=previous_code,
        error_info=error_info,
    )
