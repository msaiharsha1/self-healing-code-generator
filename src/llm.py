"""LLM integration module supporting OpenAI and Anthropic providers."""

from abc import ABC, abstractmethod

import openai
from anthropic import Anthropic

from src.config import settings
from src.logger import logger


def _clean_code(code: str) -> str:
    """Remove markdown code fences that may slip through."""
    code = code.strip()
    if code.startswith("```python"):
        code = code[9:]
    elif code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
    return code.strip()


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str, max_retries: int = 3) -> str:
        """Generate code from a prompt."""
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    """OpenAI API provider for code generation."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model

        if not self.api_key:
            raise ValueError("OpenAI API key not configured")

        self.client = openai.OpenAI(api_key=self.api_key)

    def generate(self, prompt: str, system_prompt: str, max_retries: int = 3) -> str:
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                    max_tokens=2000,
                )
                code = _clean_code(response.choices[0].message.content)
                logger.info(f"OpenAI generated {len(code)} characters")
                return code
            except Exception as e:
                logger.warning(f"OpenAI API attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise

        raise RuntimeError("Failed to generate code after all retries")


class AnthropicProvider(LLMProvider):
    """Anthropic API provider for code generation."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.anthropic_api_key
        self.model = model or settings.anthropic_model

        if not self.api_key:
            raise ValueError("Anthropic API key not configured")

        self.client = Anthropic(api_key=self.api_key)

    def generate(self, prompt: str, system_prompt: str, max_retries: int = 3) -> str:
        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    system=system_prompt,
                    messages=[{"role": "user", "content": prompt}],
                )
                code = "".join(
                    block.text for block in response.content if block.type == "text"
                )
                code = _clean_code(code)
                logger.info(f"Anthropic generated {len(code)} characters")
                return code
            except Exception as e:
                logger.warning(f"Anthropic API attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise

        raise RuntimeError("Failed to generate code after all retries")


def get_llm_provider(provider: str | None = None) -> LLMProvider:
    """Get the configured LLM provider instance."""
    provider = provider or settings.llm_provider

    if provider == "openai":
        return OpenAIProvider()
    if provider == "anthropic":
        return AnthropicProvider()
    raise ValueError(f"Unsupported LLM provider: {provider}")
