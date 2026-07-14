"""Tests for the API endpoints."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app import app
from src.models import CodeGenerationResponse


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    def test_health_root(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestRootEndpoint:
    """Test root endpoint."""

    def test_root_info(self, client):
        response = client.get("/api/v1/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Self-Healing Code Generator"
        assert data["docs"] == "/docs"


class TestGenerateEndpoint:
    """Test code generation endpoint."""

    @patch("src.api.routes.generate_validated_code")
    def test_successful_generation(self, mock_generate, client):
        mock_generate.return_value = CodeGenerationResponse(
            status="success",
            attempts=1,
            validated=True,
            code="def add(a, b):\n    return a + b",
            execution_time=0.5,
        )

        response = client.post(
            "/api/v1/generate",
            json={"prompt": "Write a function to add two numbers"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["validated"] is True
        assert "code" in data

    @patch("src.api.routes.generate_validated_code")
    def test_generation_failure(self, mock_generate, client):
        mock_generate.side_effect = RuntimeError("Failed after all retries")

        response = client.post(
            "/api/v1/generate",
            json={"prompt": "Write impossible code"},
        )

        assert response.status_code == 500
        assert "detail" in response.json()

    def test_invalid_request_empty_prompt(self, client):
        response = client.post("/api/v1/generate", json={"prompt": ""})
        assert response.status_code == 422

    def test_invalid_request_missing_prompt(self, client):
        response = client.post("/api/v1/generate", json={})
        assert response.status_code == 422

    @patch("src.api.routes.generate_validated_code")
    def test_custom_max_retries(self, mock_generate, client):
        mock_generate.return_value = CodeGenerationResponse(
            status="success",
            attempts=1,
            validated=True,
            code="print('hello')",
            execution_time=0.3,
        )

        response = client.post(
            "/api/v1/generate",
            json={"prompt": "Write hello world", "max_retries": 3},
        )

        assert response.status_code == 200
        mock_generate.assert_called_once()
        assert mock_generate.call_args[1]["max_retries"] == 3
