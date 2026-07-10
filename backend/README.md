# AI-First CRM HCP Backend

FastAPI backend for the HCP Interaction module.

## Modules

- `app/main.py`: FastAPI application factory, middleware, routers, and exception handler registration.
- `app/core/config.py`: Environment-driven settings loaded from `.env`.
- `app/shared/logging/config.py`: Central logging configuration.
- `app/shared/exceptions/`: Application exception types and global FastAPI handlers.
- `app/db/session.py`: SQLAlchemy engine, session factory, and database session dependency.
- `app/db/base.py`: SQLAlchemy declarative base and model metadata imports for Alembic.
- `app/db/repositories/`: Repository layer responsible for database queries.
- `app/domains/hcp/models/`: SQLAlchemy ORM models for HCP domain tables.
- `app/domains/hcp/schemas/`: Pydantic v2 request and response schemas.
- `app/domains/hcp/services/`: Business service layer for HCP interaction workflows.
- `app/api/deps/`: Dependency injection helpers used by routers.
- `app/api/v1/routes/`: Versioned API routers.
- `app/db/migrations/`: Alembic migration environment and generated revisions.
- `app/integrations/langgraph/`: LangGraph HCP assistant graph, state, prompts, intent router, and tool implementations.
- `app/api/v1/routes/hcp_assistant.py`: JSON chat endpoint for the React frontend at `/api/v1/hcp-assistant/chat`.

## Local Development

```bash
cd backend
uvicorn app.main:app --reload
```

Swagger UI is available at `/docs`.

## Groq Models

The backend reads `GROQ_API_KEY`, `GROQ_MODEL`, and `GROQ_FALLBACK_MODEL` from `.env`.

`gemma2-9b-it` is configured as the primary model for this project. Groq currently reports that model as decommissioned, so the LangGraph integration supports `llama-3.1-8b-instant` as a fallback model.
