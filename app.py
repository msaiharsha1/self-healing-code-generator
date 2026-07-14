"""FastAPI application entry point for the Self-Healing Code Generator."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router
from src.config import settings
from src.logger import logger

# Ensure logs directory exists
Path(settings.log_file).parent.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting Self-Healing Code Generator API")
    logger.info(f"Using LLM provider: {settings.llm_provider}")
    logger.info(f"Max retries: {settings.max_retries}")
    logger.info(f"Execution timeout: {settings.execution_timeout}s")
    yield
    logger.info("Shutting down Self-Healing Code Generator API")


app = FastAPI(
    title="Self-Healing Code Generator",
    description="Automatically generates, validates, and repairs Python code from natural language prompts.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")
app.include_router(router)


def main():
    """Run the application using uvicorn."""
    import uvicorn

    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()
