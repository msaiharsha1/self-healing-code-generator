"""Utility functions for the application."""

import hashlib
import re
from datetime import datetime


def extract_code_blocks(text: str) -> list[str]:
    """Extract code blocks from markdown-formatted text."""
    pattern = r"```(?:python)?\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    return [m.strip() for m in matches]


def clean_code(code: str) -> str:
    """Clean code by removing markdown fences and excess whitespace."""
    code = re.sub(r"^```(?:python)?\n", "", code)
    code = re.sub(r"\n```$", "", code)
    lines = [line.rstrip() for line in code.split("\n")]
    code = "\n".join(lines)
    code = re.sub(r"\n{3,}", "\n\n", code)
    return code.strip()


def hash_code(code: str) -> str:
    """Generate a SHA256 hash for code deduplication."""
    return hashlib.sha256(code.encode()).hexdigest()


def format_timestamp(dt: datetime | None = None) -> str:
    """Format a datetime object as an ISO string."""
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat()


def truncate_string(s: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate a string to a maximum length."""
    if len(s) <= max_length:
        return s
    return s[: max_length - len(suffix)] + suffix
