# AI-First CRM HCP Module

## Overview

AI-First CRM HCP Module is a full-stack healthcare CRM workflow for logging Healthcare Professional (HCP) interactions with AI assistance. The React interface combines a structured interaction form with an AI chat assistant that extracts CRM-ready data from natural language. The FastAPI backend persists interaction records in PostgreSQL and exposes CRUD APIs plus a LangGraph-powered assistant endpoint. Groq provides LLM inference with a production fallback model path.

## Features

- AI-powered HCP interaction logging
- Edit interactions
- Search interaction history
- Summarize interactions
- Suggest follow-up actions
- Automatic structured form autofill
- PostgreSQL persistence
- LangGraph agent
- Groq LLM integration

## Tech Stack

| Layer | Technologies |
| --- | --- |
| Frontend | React, Redux Toolkit, TypeScript, Material UI, Vite |
| Backend | FastAPI, SQLAlchemy, Alembic |
| Database | PostgreSQL, Neon compatible |
| AI | LangGraph, Groq, `gemma2-9b-it` primary, `llama-3.1-8b-instant` fallback |

## Architecture

```text
User
  |
  v
React
  |
  v
FastAPI
  |
  v
LangGraph
  |
  v
Groq LLM
  |
  v
CRUD Repository
  |
  v
PostgreSQL
```

## Project Structure

```text
.
+-- backend/
|   +-- app/
|   |   +-- api/
|   |   +-- core/
|   |   +-- db/
|   |   +-- domains/hcp/
|   |   +-- integrations/langgraph/
|   |   +-- shared/
|   +-- scripts/
|   +-- alembic.ini
|   +-- pyproject.toml
+-- frontend/
|   +-- src/
|   |   +-- app/
|   |   +-- features/hcp/
|   |   +-- store/
|   |   +-- styles/
|   |   +-- theme/
|   +-- package.json
|   +-- vite.config.ts
+-- docker-compose.yml
+-- .env.example
+-- README.md
```

## Setup

### 1. Clone

```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# Install dependencies
python -m pip install -e .

# Run migrations
alembic upgrade head

# Start FastAPI
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. Environment Variables

Create a `.env` file from `.env.example` and set local values.

```env
# Backend
ENVIRONMENT=local
PROJECT_NAME=AI-First CRM HCP API
API_V1_PREFIX=/api/v1
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/ai_first_crm

CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
LOG_LEVEL=INFO

# Frontend
VITE_API_BASE_URL=http://localhost:8000/api/v1

# AI
GROQ_API_KEY=
GROQ_MODEL=gemma2-9b-it
GROQ_FALLBACK_MODEL=llama-3.1-8b-instant
```

### 5. Run

| Service | URL |
| --- | --- |
| Backend | `http://localhost:8000` |
| Swagger | `http://localhost:8000/docs` |
| OpenAPI JSON | `http://localhost:8000/api/v1/openapi.json` |
| Frontend | `http://localhost:5173` |

## Example AI Prompt

```text
Met Dr. Sharma today at 3 PM. We discussed CardioMax efficacy. Shared product brochure. He responded positively and requested a follow-up meeting next Friday.
```

The AI assistant classifies the intent, extracts structured fields, logs the interaction, persists it in PostgreSQL, and returns JSON that autofills the React form.

## API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/hcp-assistant/chat` | LangGraph AI assistant chat |
| POST | `/api/v1/hcp-interactions` | Create HCP interaction |
| GET | `/api/v1/hcp-interactions` | List/search HCP interactions |
| GET | `/api/v1/hcp-interactions/{interaction_id}` | Get interaction by ID |
| PATCH | `/api/v1/hcp-interactions/{interaction_id}` | Update interaction |
| DELETE | `/api/v1/hcp-interactions/{interaction_id}` | Delete interaction |

## Notes

- Groq automatically falls back to `llama-3.1-8b-instant` because `gemma2-9b-it` is currently unavailable.
- Docker Compose is included for local PostgreSQL, and Neon PostgreSQL is also supported through `DATABASE_URL`.
- Real credentials belong in `.env`; `.env.example` contains placeholders only.

## License

MIT
