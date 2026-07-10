# AI-First CRM HCP Module

Production-oriented project scaffold for an AI-first Healthcare Professional (HCP) CRM module.

This repository includes the HCP interaction UI, FastAPI CRUD backend, PostgreSQL persistence, and a LangGraph-powered HCP assistant endpoint.

## Tech Stack

- Frontend: React, Vite, Redux Toolkit, Material UI
- Backend: FastAPI, SQLAlchemy
- Database: PostgreSQL
- AI Framework: LangGraph
- LLM Provider/Model: Groq `gemma2-9b-it`
- LLM Fallback: Groq currently reports `gemma2-9b-it` as decommissioned, so the backend supports `llama-3.1-8b-instant` as a configurable fallback model.
- Font: Google Inter

## Project Structure

```text
ai-first-crm-hcp/
+-- backend/
|   +-- app/
|   |   +-- api/
|   |   |   +-- deps/
|   |   |   +-- v1/
|   |   |       +-- routes/
|   |   +-- core/
|   |   +-- db/
|   |   |   +-- migrations/
|   |   |   +-- repositories/
|   |   +-- domains/
|   |   |   +-- hcp/
|   |   |       +-- models/
|   |   |       +-- schemas/
|   |   |       +-- services/
|   |   |       +-- use_cases/
|   |   +-- integrations/
|   |   |   +-- groq/
|   |   |   +-- langgraph/
|   |   |       +-- agents/
|   |   |       +-- graphs/
|   |   |       +-- state/
|   |   +-- shared/
|   |   |   +-- exceptions/
|   |   |   +-- logging/
|   |   |   +-- security/
|   |   +-- tests/
|   |       +-- integration/
|   |       +-- unit/
|   +-- scripts/
|   +-- pyproject.toml
+-- frontend/
|   +-- public/
|   |   +-- fonts/
|   +-- src/
|   |   +-- app/
|   |   +-- assets/
|   |   +-- components/
|   |   |   +-- common/
|   |   |   +-- layout/
|   |   +-- config/
|   |   +-- features/
|   |   |   +-- hcp/
|   |   |       +-- api/
|   |   |       +-- components/
|   |   |       +-- hooks/
|   |   |       +-- pages/
|   |   |       +-- slices/
|   |   |       +-- types/
|   |   +-- hooks/
|   |   +-- lib/
|   |   +-- routes/
|   |   +-- services/
|   |   +-- store/
|   |   +-- styles/
|   |   +-- theme/
|   |   +-- tests/
|   +-- package.json
|   +-- vite.config.ts
+-- infra/
|   +-- docker/
|   +-- postgres/
+-- docs/
|   +-- architecture/
|   +-- api/
|   +-- decisions/
+-- .env.example
+-- .gitignore
+-- docker-compose.yml
```

## Folder Explanation

### `backend/`

Backend service boundary for the FastAPI application. This folder owns HTTP APIs, business orchestration, persistence, AI integrations, and backend tests.

### `backend/app/`

Main Python application package. All importable backend source code should live under this package.

### `backend/app/api/`

API layer for FastAPI routers, dependency wiring, request-level concerns, and versioned route registration.

### `backend/app/api/deps/`

Reusable FastAPI dependencies such as database sessions, authentication context, tenant context, request tracing, and permissions.

### `backend/app/api/v1/routes/`

Versioned API route modules. HCP-specific endpoints will be added here later without mixing route logic into domain services.

### `backend/app/core/`

Application-wide configuration and runtime setup, such as environment settings, CORS, app lifecycle, constants, and dependency container wiring.

### `backend/app/db/`

Database infrastructure for SQLAlchemy setup, PostgreSQL sessions, base metadata, migration integration, and persistence helpers.

### `backend/app/db/migrations/`

Alembic migration files will live here once database schemas are introduced.

### `backend/app/db/repositories/`

Repository classes for database access patterns. This keeps SQLAlchemy queries out of API routes and higher-level use cases.

### `backend/app/domains/`

Domain-oriented business modules. Each domain should own its models, schemas, services, and use cases.

### `backend/app/domains/hcp/`

HCP CRM domain boundary. Future HCP entities, validation schemas, workflows, and business rules will be added here.

### `backend/app/domains/hcp/models/`

SQLAlchemy ORM models for HCP-related database tables.

### `backend/app/domains/hcp/schemas/`

Pydantic request and response schemas for HCP APIs and service contracts.

### `backend/app/domains/hcp/services/`

Domain services for reusable HCP business behavior.

### `backend/app/domains/hcp/use_cases/`

Application-level orchestration for specific HCP workflows. Use cases coordinate repositories, services, and AI agents.

### `backend/app/integrations/`

External system integration boundary. Provider-specific code lives here instead of leaking into domain logic.

### `backend/app/integrations/groq/`

Groq client configuration and LLM adapter code will live here, including the `gemma2-9b-it` model integration.

### `backend/app/integrations/langgraph/`

LangGraph-specific orchestration layer for state definitions, graphs, nodes, and agents.

### `backend/app/integrations/langgraph/agents/`

Future AI agents for HCP workflows.

### `backend/app/integrations/langgraph/graphs/`

LangGraph graph definitions and workflow composition.

### `backend/app/integrations/langgraph/state/`

Shared graph state types and checkpoint-related structures.

### `backend/app/shared/`

Cross-cutting backend utilities that are not owned by a single domain.

### `backend/app/shared/exceptions/`

Custom exception classes and exception mapping.

### `backend/app/shared/logging/`

Structured logging setup and request correlation helpers.

### `backend/app/shared/security/`

Security utilities such as token validation, password helpers, RBAC primitives, and audit helpers.

### `backend/app/tests/`

Backend test suite, split by unit and integration tests.

### `backend/scripts/`

Operational scripts for backend tasks such as local setup, migration helpers, seed scripts, and maintenance commands.

### `frontend/`

Frontend application boundary for the React + Vite client.

### `frontend/public/`

Static files served by Vite without bundling.

### `frontend/public/fonts/`

Local font assets if Inter is self-hosted later. The project can also load Inter from Google Fonts through the frontend entrypoint.

### `frontend/src/`

Main frontend source root.

### `frontend/src/app/`

Application bootstrap concerns such as app providers, root shell composition, and global initialization.

### `frontend/src/assets/`

Images, icons, static SVGs, and other frontend assets imported by React components.

### `frontend/src/components/`

Shared UI components used across multiple features.

### `frontend/src/components/common/`

Generic reusable components such as buttons, loaders, empty states, and form controls.

### `frontend/src/components/layout/`

Layout components such as navigation, page shell, sidebar, header, and content containers.

### `frontend/src/config/`

Frontend runtime configuration, environment mappings, API base URLs, and constants.

### `frontend/src/features/`

Feature-sliced frontend modules. Each feature owns its UI, API calls, Redux slices, hooks, and types.

### `frontend/src/features/hcp/`

HCP CRM feature boundary. Screens, state, API bindings, and UI specific to HCP workflows will be added here.

### `frontend/src/features/hcp/api/`

HCP-specific frontend API client functions.

### `frontend/src/features/hcp/components/`

HCP-specific React components.

### `frontend/src/features/hcp/hooks/`

HCP-specific React hooks.

### `frontend/src/features/hcp/pages/`

Route-level HCP pages.

### `frontend/src/features/hcp/slices/`

Redux Toolkit slices for HCP state.

### `frontend/src/features/hcp/types/`

TypeScript types for the HCP frontend feature.

### `frontend/src/hooks/`

Reusable application-wide React hooks.

### `frontend/src/lib/`

Frontend utility libraries and wrappers around third-party packages.

### `frontend/src/routes/`

Route declarations and route guards.

### `frontend/src/services/`

Shared frontend services such as HTTP client setup, auth transport, telemetry, and error handling.

### `frontend/src/store/`

Redux Toolkit store configuration and shared store utilities.

### `frontend/src/styles/`

Global CSS, reset styles, and base typography.

### `frontend/src/theme/`

Material UI theme configuration, design tokens, palette, typography, and component overrides.

### `frontend/src/tests/`

Frontend test setup and shared testing utilities.

### `infra/`

Infrastructure and local environment assets.

### `infra/docker/`

Dockerfiles and container-specific configuration.

### `infra/postgres/`

PostgreSQL initialization scripts and database-local configuration.

### `docs/`

Project documentation.

### `docs/architecture/`

Architecture diagrams, module boundaries, and system design notes.

### `docs/api/`

API documentation, request/response contracts, and integration notes.

### `docs/decisions/`

Architecture Decision Records (ADRs) for important technical choices.
