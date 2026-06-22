# Architecture and Optimization Decisions

## Architecture

The service follows a layered architecture:

```text
FastAPI Routers
    ↓
Service Layer
    ↓
SQLAlchemy / Raw SQL
    ↓
PostgreSQL