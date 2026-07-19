# Containerized Task Management API

Task API is a clean, container-friendly FastAPI service for managing tasks with layered architecture, SQLAlchemy ORM, PostgreSQL persistence, and interactive API documentation.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)](https://sqlalchemy.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docker.com)

---

## Overview

This project demonstrates a practical backend architecture built around FastAPI and SQLAlchemy. It supports full CRUD operations for tasks, switches between PostgreSQL and an in-memory repository depending on environment configuration, and exposes Swagger UI for testing endpoints directly in the browser.

### What makes this project strong

- Clean separation of concerns: routes, service layer, repository abstraction
- Database-backed persistence with PostgreSQL via Docker
- Flexible storage mode for development and testing
- Automatic schema creation and seed data on startup
- Ready-to-use API docs at `/docs`

---

## Architecture

```mermaid
flowchart LR
    Client[Client / Browser / curl] --> Router[FastAPI routes
    in app/routes.py]
    Router --> Service[TaskService
    in app/service.py]
    Service --> Repo[TaskRepository abstraction
    in app/repository.py]
    Repo --> SQL[SQLAlchemyTaskRepository]
    Repo --> Mem[InMemoryTaskRepository]
    SQL --> PG[(PostgreSQL)]
    Mem --> RAM[(In-memory store)]
    Main[main.py lifespan] --> SQL
    Main --> Mem
    Compose[Docker Compose] --> App[FastAPI container]
    Compose --> PG
    Compose --> Redis[(Redis service)]
```

### Request flow

1. A request enters the FastAPI app through the router layer.
2. The service layer handles validation and business rules.
3. The repository layer persists data using either SQLAlchemy with PostgreSQL or an in-memory backend.
4. Responses are serialized through Pydantic models and returned to the client.

---

## Features

- Full CRUD support for tasks
- Pydantic-based request and response validation
- SQLAlchemy ORM integration for database operations
- Two storage modes:
  - PostgreSQL when `DATABASE_URL` is configured
  - In-memory storage for local development without Docker
- Health and stats endpoints
- Automatic startup seeding of example tasks

---

## Tech Stack

| Technology | Purpose |
|---|---|
| FastAPI | Web framework and API routing |
| Uvicorn | ASGI server |
| SQLAlchemy | ORM and database abstraction |
| PostgreSQL | Persistent relational data store |
| Pydantic | Validation and serialization |
| Docker Compose | Containerized app and database orchestration |
| Redis | Included as a service for future extension work |

---

## Quick Start

### Option 1: Docker (recommended)

```bash
cp .env.example .env
docker compose up --build
```

Then open:

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

The first startup will:

- launch PostgreSQL and Redis services
- create the required table automatically with SQLAlchemy
- seed example tasks if the database is empty

### Option 2: Local Python (in-memory mode)

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

The app will run without Docker and use in-memory storage when `DATABASE_URL` is not set.

---

## Environment Configuration

The project uses environment variables from [.env.example](.env.example) as the template.

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string in SQLAlchemy format. If omitted, the app falls back to in-memory storage. |
| `REDIS_URL` | Redis connection string for future integration work. |

Example:

```env
DATABASE_URL=postgresql+psycopg2://taskuser:taskpass@localhost:5432/tasks
REDIS_URL=redis://localhost:6379/0
```

---

## API Reference

### Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | API metadata and current storage mode |
| GET | `/health` | Health check |
| GET | `/stats` | Returns total, done, and open task counts |
| GET | `/tasks/` | List all tasks |
| GET | `/tasks/{task_id}` | Retrieve one task by ID |
| POST | `/tasks/` | Create a new task |
| PUT | `/tasks/{task_id}` | Update an existing task |
| DELETE | `/tasks/{task_id}` | Delete a task |

### Example requests

Create a task:

```bash
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries"}'
```

List tasks:

```bash
curl http://localhost:8000/tasks/
```

Update a task:

```bash
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"done": true}'
```

Delete a task:

```bash
curl -X DELETE http://localhost:8000/tasks/1
```

---

## Project Structure

```text
task-api-v2/
├── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── dependencies.py
│   ├── memory_repo.py
│   ├── models.py
│   ├── repository.py
│   ├── routes.py
│   ├── service.py
│   └── sqlalchemy_repo.py
└── packages/
```

---

## Docker Commands

```bash
docker compose up --build
docker compose up -d
docker compose logs -f
docker compose down
docker compose down -v
```

To inspect the database directly:

```bash
docker compose exec db psql -U taskuser -d tasks
```

---

## Notes

- The app creates the database schema automatically during startup through SQLAlchemy.
- The repository abstraction makes the service layer independent from the storage backend.
- The current implementation is focused on task CRUD and persistence, with Redis included as part of the Docker environment for future enhancements.

---

Built for the FlyRank internship workflow as a structured FastAPI backend example.
