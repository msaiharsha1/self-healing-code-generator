"""API routes for the FastAPI application."""

from fastapi import APIRouter, HTTPException

from src.healer import generate_validated_code
from src.logger import logger
from src.models import CodeGenerationRequest, CodeGenerationResponse, HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy")


@router.post("/generate", response_model=CodeGenerationResponse, tags=["Code Generation"])
async def generate_code(request: CodeGenerationRequest) -> CodeGenerationResponse:
    """
    Generate and validate Python code from a natural language prompt.

    Workflow: LLM generation -> AST validation -> sandbox execution ->
    automatic repair loop -> validated code returned.
    """
    logger.info(f"Received code generation request: {request.prompt[:100]}...")

    try:
        response = await generate_validated_code(
            prompt=request.prompt,
            llm_provider=request.llm_provider,
            max_retries=request.max_retries,
        )

        logger.info(
            f"Code generation successful in {response.attempts} attempts, "
            f"{response.execution_time:.2f}s"
        )
        return response

    except RuntimeError as e:
        logger.error(f"Code generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": str(e), "type": "generation_failed"},
        )

    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": str(e), "type": "invalid_request"},
        )

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": "Internal server error", "type": "internal_error"},
        )


@router.get("/", tags=["Root"])
async def root() -> dict:
    """Root endpoint with API information."""
    return {
        "service": "Self-Healing Code Generator",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
