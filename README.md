# Task API

A production-ready REST API for task management built with **FastAPI**, **SQLAlchemy ORM**, **PostgreSQL**, and **Docker**.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)](https://sqlalchemy.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docker.com)

---

## ✨ Features

- Full **CRUD** — create, read, update, delete tasks
- **SQLAlchemy ORM** — no raw SQL strings; Python objects map to DB rows
- **Two storage backends** — PostgreSQL (Docker) or in-memory (no Docker needed)
- **Persistent data** — survives app and container restarts via Docker volumes
- **Auto-generated Swagger UI** at `/docs` — test every endpoint in the browser
- **Clean architecture** — routes → service → repository; swap storage without touching routes

---

## 🚀 Quick Start

### Option A — Docker (Recommended, full persistence)

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Start everything (Postgres + Redis + FastAPI)
docker compose up

# 3. Open in your browser
# API docs (Swagger UI):  http://localhost:8000/docs
# Health check:           http://localhost:8000/health
```

First run automatically:
- Starts PostgreSQL and waits for it to be ready
- Creates the `tasks` table via SQLAlchemy
- Seeds 3 example tasks
- Starts the FastAPI server

### Option B — Local Python (no Docker, in-memory storage)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the app (no .env needed — uses in-memory storage)
uvicorn main:app --reload

# 3. Open http://localhost:8000/docs
```

Data resets on every restart. Perfect for learning without Docker.

---

## 📡 API Reference

### Endpoints

| Method | Path | Status | Description |
|--------|------|--------|-------------|
| `GET` | `/` | 200 | API info and storage mode |
| `GET` | `/health` | 200 | Health check |
| `GET` | `/stats` | 200 | Task statistics (total / done / open) |
| `GET` | `/tasks/` | 200 | List all tasks |
| `GET` | `/tasks/{id}` | 200, 404 | Get one task |
| `POST` | `/tasks/` | 201, 400 | Create a task |
| `PUT` | `/tasks/{id}` | 200, 400, 404 | Update title and/or done |
| `DELETE` | `/tasks/{id}` | 204, 404 | Delete a task |

### Request / Response Examples

**Create a task**
```bash
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries"}'
```
```json
// HTTP 201 Created
{"id": 4, "title": "Buy groceries", "done": false}
```

**List all tasks**
```bash
curl http://localhost:8000/tasks/
```
```json
// HTTP 200 OK
[
  {"id": 1, "title": "Buy groceries", "done": false},
  {"id": 2, "title": "Read a book",   "done": true},
  {"id": 3, "title": "Go for a walk", "done": false}
]
```

**Mark a task done**
```bash
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"done": true}'
```
```json
// HTTP 200 OK
{"id": 1, "title": "Buy groceries", "done": true}
```

**Delete a task**
```bash
curl -X DELETE http://localhost:8000/tasks/1
# HTTP 204 No Content (empty body)
```

**Error responses**
```bash
curl http://localhost:8000/tasks/999
# HTTP 404 → {"detail": "Task 999 not found"}

curl -X POST http://localhost:8000/tasks/ -H "Content-Type: application/json" -d '{}'
# HTTP 422 → Pydantic validation error (missing title)

curl -X POST http://localhost:8000/tasks/ -H "Content-Type: application/json" -d '{"title":""}'
# HTTP 400 → {"detail": "title must not be empty"}
```

---

## 📁 Project Structure

```
task-api/
├── main.py                  ← FastAPI app + startup (create tables, seed data)
├── requirements.txt         ← Python dependencies
├── Dockerfile               ← Build the app container
├── docker-compose.yml       ← Orchestrate app + Postgres + Redis
├── .env.example             ← Config template (committed to Git)
├── .env                     ← Your secrets (gitignored)
├── .gitignore
│
└── app/
    ├── __init__.py
    ├── models.py            ← TaskORM (SQLAlchemy) + Task/TaskCreate/TaskUpdate (Pydantic)
    ├── database.py          ← Engine, SessionLocal, get_db() dependency
    ├── repository.py        ← Abstract interface (5-method contract)
    ├── memory_repo.py       ← In-memory implementation (Python list)
    ├── sqlalchemy_repo.py   ← SQLAlchemy ORM implementation (PostgreSQL)
    ├── service.py           ← Business logic and validation
    ├── routes.py            ← HTTP endpoints
    └── dependencies.py      ← Wires repo + service via FastAPI Depends()
```

---

## 🏗️ Architecture

### Layers

```
HTTP Request
     ↓
routes.py          — parse URL, HTTP method, status codes
     ↓
service.py         — business rules, validation
     ↓
repository.py      — abstract interface (contract)
     ↓
┌────────────────────────────────┐
│ SQLAlchemyTaskRepository       │  (when DATABASE_URL is set)
│   → ORM queries → PostgreSQL   │
├────────────────────────────────┤
│ InMemoryTaskRepository         │  (when DATABASE_URL is not set)
│   → Python list                │
└────────────────────────────────┘
```

### SQLAlchemy ORM vs Raw SQL

| Task | Raw SQL (old) | SQLAlchemy ORM (new) |
|------|--------------|----------------------|
| Get all | `cur.execute("SELECT * FROM tasks")` | `db.query(TaskORM).all()` |
| Get one | `cur.execute("SELECT ... WHERE id = %s", (id,))` | `db.query(TaskORM).filter(TaskORM.id == id).first()` |
| Create | `cur.execute("INSERT INTO tasks ... RETURNING *")` | `db.add(TaskORM(...)); db.commit()` |
| Update | `cur.execute("UPDATE tasks SET ... WHERE id = %s")` | `task.title = "new"; db.commit()` |
| Delete | `cur.execute("DELETE FROM tasks WHERE id = %s")` | `db.delete(task); db.commit()` |

### What Changed Between W2 and BE-04

| W2 | BE-04 |
|----|-------|
| One flat `main.py` | Layered: routes / service / repo |
| In-memory Python list | PostgreSQL via SQLAlchemy ORM |
| Data lost on restart | Data persists across restarts |
| No Docker | Docker Compose (one command) |
| `next_id` counter | `SERIAL` auto-increment in Postgres |

The routes are **identical** between W2 and BE-04 — same paths, same status codes, same JSON. Only storage changed.

---

## 💾 Data Persistence Demo

```bash
# Start the stack
docker compose up -d

# Create a task
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title": "This will survive a restart"}'
# → {"id": 4, "title": "This will survive a restart", "done": false}

# Completely stop and remove all containers
docker compose down

# Start again from scratch
docker compose up -d

# Task is still there ✅
curl http://localhost:8000/tasks/4
# → {"id": 4, "title": "This will survive a restart", "done": false}
```

**Why?** The `postgres_data` named volume stores Postgres data files on your machine. `docker compose down` removes containers but never touches volumes.

---

## 🐳 Docker Reference

```bash
# Start everything (foreground — see logs)
docker compose up

# Start in background
docker compose up -d

# Watch logs
docker compose logs -f
docker compose logs -f app    # app only
docker compose logs -f db     # postgres only

# Stop (keeps data)
docker compose down

# Stop AND delete all data (fresh start)
docker compose down -v

# Rebuild after code changes
docker compose up --build

# Connect to Postgres directly
docker compose exec db psql -U taskuser -d tasks

# Open a shell in the app container
docker compose exec app bash
```

---

## 🗄️ Database

SQLAlchemy creates and manages the schema automatically. No SQL files to run.

```python
# This runs on every app startup (creates table if not exists):
Base.metadata.create_all(bind=engine)
```

To inspect the database directly:

```bash
docker compose exec db psql -U taskuser -d tasks

# Inside psql:
\dt              -- list tables
\d tasks         -- describe tasks table
SELECT * FROM tasks;
SELECT COUNT(*) FROM tasks;
\q               -- quit
```

---

## ⚙️ Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | *(not set)* | SQLAlchemy connection string. If missing, uses in-memory storage. |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection (stretch goal, W4) |

**Format for `DATABASE_URL`:**
```
postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DBNAME
```

For Docker Compose, this is already set in `docker-compose.yml`:
```
DATABASE_URL=postgresql+psycopg2://taskuser:taskpass@db:5432/tasks
```

---

## 🔧 Troubleshooting

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| `Connection refused` on port 8000 | App not running | `docker compose up` |
| `could not connect to server` | Postgres not ready | Wait 10s, try again |
| `port 5432 already in use` | Local Postgres running | `docker compose stop db` or stop local Postgres |
| `port 8000 already in use` | Another server on 8000 | Stop it, or change port in compose file |
| Data disappeared | Not using Docker volume | `docker compose up` (not `uvicorn`) |
| 422 Validation Error | Request body malformed | Check JSON, add `Content-Type: application/json` |

---

## 🛠️ Tech Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| **FastAPI** | 0.115 | Web framework, auto-docs |
| **SQLAlchemy** | 2.0 | ORM, DB schema management |
| **PostgreSQL** | 16 | Persistent relational database |
| **psycopg2** | 2.9 | Python → Postgres driver |
| **Pydantic** | 2.x | JSON validation and serialization |
| **Uvicorn** | 0.32 | ASGI web server |
| **Docker Compose** | V2 | Container orchestration |
| **Redis** | 7 | Caching (W4 stretch goal) |

---

## 📚 Learning Path

| Week | What was added |
|------|---------------|
| W2 | FastAPI basics, CRUD, in-memory storage, Swagger UI |
| BE-04 | Docker, PostgreSQL, SQLAlchemy ORM, data persistence |
| W4 | Redis caching, background tasks |
| W5+ | Auth, pagination, migrations, deployment |

---

*Built during FlyRank Backend Internship — Week 3 Assignment BE-04*
