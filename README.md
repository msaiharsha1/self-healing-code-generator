# Self-Healing Code Generator

A FastAPI service that generates Python code from natural language prompts, validates it, and automatically repairs any errors before returning it.

## How it works

1. An LLM (OpenAI or Anthropic) generates code from your prompt
2. Syntax is checked with Python's AST module
3. The code runs in an isolated subprocess sandbox
4. If anything fails, the error is fed back to the LLM to fix
5. The loop repeats until the code is valid (or max retries is reached)

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your API key here
```

## Run

```bash
uvicorn app:app --reload
```

Open http://localhost:8000/docs for the interactive API docs.

## Usage

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a Python function for quicksort"}'
```

## Tests

```bash
pytest
```

## Tech stack

Python 3.12 · FastAPI · Pydantic · OpenAI / Anthropic APIs
