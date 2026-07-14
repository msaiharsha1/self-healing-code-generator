"""Pydantic models for request/response validation and data transfer."""

from datetime import datetime
from pydantic import BaseModel, Field


class CodeGenerationRequest(BaseModel):
    """Request model for the code generation endpoint."""

    prompt: str = Field(..., min_length=1, max_length=5000)
    max_retries: int | None = Field(default=None, ge=1, le=10)
    llm_provider: str | None = Field(default=None)


class CodeGenerationResponse(BaseModel):
    """Response model for the code generation endpoint."""

    status: str
    attempts: int
    validated: bool
    code: str
    execution_time: float | None = None
    error: str | None = None


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"


class ValidationResult(BaseModel):
    """Result of code validation."""

    success: bool
    error_type: str | None = None
    error_message: str | None = None
    stdout: str | None = None
    stderr: str | None = None
    traceback: str | None = None


class RepairAttempt(BaseModel):
    """Tracks a single repair attempt."""

    attempt_number: int
    code: str
    syntax_valid: bool
    runtime_valid: bool | None = None
    error: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class GenerationHistory(BaseModel):
    """Complete history of a code generation session."""

    prompt: str
    attempts: list[RepairAttempt] = Field(default_factory=list)
    final_code: str | None = None
    success: bool = False
    total_time: float | None = None
