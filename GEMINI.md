# Project Overview

This is a FastAPI application that provides a RESTful API for managing products, tasks, and customers. It implements an **Enterprise-Grade Modular Architecture** designed for scalability, maintainability, and observability.

# Architecture & Patterns

## 1. Modular Design ((app/modules/))
The project is structured by domains (DDD-lite). Each module (e.g., tasks, products) contains unrelated vertical slices:
- routers.py: API Endpoints.
- service.py: Business Logic.
- repository.py: Data Access Layer.
- models.py: Database Entities (SQLModel).
- schemas.py: DTOs (Pydantic).

## 2. Repository Pattern ((app/core/repository.py))
Decouples data access from business logic.
- BaseRepository: Generic CRUD (Create, Get, Update, Delete).
- ModuleRepository: Specific domain queries.

## 3. Centralized Exception Handling ((app/core/handlers.py))
Custom exceptions ((NotFoundException, BadRequestException)) are raised by Services and caught by global handlers to return standardized JSON error responses.

## 4. Typed Configuration ((app/core/config.py))
Uses pydantic-settings to load environment variables.
- Access: from app.core.config import settings

## 5. Database Migrations ((alembic/))
Uses **Alembic** for schema version control.
- Env Setup: alembic/env.py reads settings.DATABASE_URL and SQLModel.metadata.
- Workflow:
    - Edit models.py.
    - alembic revision --autogenerate -m "desc"
    - alembic upgrade head

## 6. Automated Testing ((tests/))
Uses **pytest** and **TestClient**.
- Integration tests run against an **In-Memory SQLite** database ((tests/conftest.py)) to ensure speed and isolation.
- Command: pytest

## 7. Code Quality ((ruff.toml, mypy.ini))
Enforced via CI/CD-ready tools:
- **Ruff**: Fast linting and formatting (replaces Black/Isort).
    - ruff check .
    - ruff format .
- **MyPy**: Static type checking.
    - mypy .

## 8. Structured Logging ((app/core/logging.py))
Uses **structlog**.
- JSON logs in production, colored logs in development.
- **Request ID**: Middleware ((app/main.py)) generates a request_id for every request and binds it to the logger context for traceability.

## 9. Security & Authentication ((app/auth/))
Implements **Enterprise-Grade JWT Security** and **RBAC**:
- **Token Rotation**: Refresh tokens are rotated (invalidated) on every use.
- **Robust Logout**: Tokens are revoked via blacklist (`UserRevokedToken`) upon logout.
- **RBAC System**: Granular permission control per Module.
    - **PermissionChecker**: Dependency verifies aggregated permissions from all user roles.
    - **Implicit Read**: Assigning a module to a role grants read access.
    - **Superuser**: Bypasses all RBAC key checks.
    - **Docs**: `docs/RBAC_GUIDE.md` and `docs/AUTHENTICATION_GUIDE.md`.

## 10. Database Migrations (Alembic)
- **Critical**: Models MUST be imported in `alembic/env.py` to be detected.
- **Workflow**: Edit Model -> Register in env.py -> Generate (`--autogenerate`) -> Apply (`upgrade head`).
- **Docs**: `docs/ALEMBIC_GUIDE.md`.

## 11. Audit System (Enterprise Logging)
- **Comprehensive Tracking**: Logs both **Access** (via Middleware) and **Data Changes** (CDC via SQLAlchemy Hooks).
- **Architecture**:
    - **Access**: Logs User, IP, Path, Status Code for every request.
    - **CDC**: Logs `old` vs `new` values for `INSERT`, `UPDATE`, `DELETE`.
    - **Cold Storage**: Script to archive and prune old logs (`scripts/archive_audit.py`).
- **Docs**: `docs/AUDIT_GUIDE.md`.

# Development Workflow

## Setup
1. Clone & Venv.
2. pip install -r requirements.txt.
3. cp .env.example .env.
4. alembic upgrade head (Apply migrations).
5. python seeds/seed_create_app.py (Optional seeds).

## Running
```bash
fastapi dev app/main.py
```
- **Docs**: `/docs` (Swagger) and `/redoc` (Custom CDN version to avoid errors).
- **Index**: Landing page at `/`.

## Testing & Quality
```bash
pytest          # Run tests
ruff check .    # Lint
ruff format .   # Format
mypy .          # Type check
```
