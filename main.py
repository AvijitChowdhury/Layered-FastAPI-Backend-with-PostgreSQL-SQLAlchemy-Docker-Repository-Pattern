# ============================================================
# main.py — Application entrypoint
#
# Responsibilities:
#   1. Create the FastAPI app
#   2. On startup: create all DB tables (SQLAlchemy does this)
#      and seed 3 example tasks if the table is empty
#   3. Mount the task router (/tasks/*)
#   4. Define global endpoints (/, /health, /stats)
# ============================================================

from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager

from app.routes import router as tasks_router
from app.service import TaskService
from app.dependencies import get_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once on startup before the server starts accepting requests.

    WHAT HAPPENS HERE:
    1. Base.metadata.create_all(engine)
       SQLAlchemy reads all classes that inherit from Base (only TaskORM
       right now) and runs CREATE TABLE IF NOT EXISTS for each one.
       This is the ORM equivalent of running init.sql manually.

    2. Seed 3 example tasks if the table is empty.
       Uses a fresh DB session opened just for this setup work.

    The 'yield' hands control to FastAPI — everything after yield
    runs on shutdown (nothing to clean up here).
    """
    from app.database import engine, SessionLocal
    from app.models import Base, TaskORM

    # ── Create tables ─────────────────────────────────────────
    # checkfirst=True is implied by IF NOT EXISTS — safe to rerun
    Base.metadata.create_all(bind=engine)

    # ── Seed example data ─────────────────────────────────────
    db = SessionLocal()
    try:
        if db.query(TaskORM).count() == 0:
            # Table is empty (first run) — add seed rows
            seeds = [
                TaskORM(title="Buy groceries", done=False),
                TaskORM(title="Read a book",   done=True),
                TaskORM(title="Go for a walk", done=False),
            ]
            db.add_all(seeds)
            db.commit()
    finally:
        db.close()

    yield   # server is now running and accepting requests


# ── Create app ────────────────────────────────────────────────
app = FastAPI(
    title="Task API",
    description=(
        "CRUD API for tasks — FastAPI + SQLAlchemy ORM + PostgreSQL + Docker.\n\n"
        "Storage: **PostgreSQL** when `DATABASE_URL` is set, "
        "**in-memory** otherwise.\n\n"
        "Try the full CRUD cycle using the endpoints below."
    ),
    version="3.0",
    lifespan=lifespan,
)

app.include_router(tasks_router)


# ── Global endpoints ──────────────────────────────────────────

@app.get("/", tags=["info"], summary="API info")
def root():
    from app.database import DATABASE_URL
    return {
        "name":    "Task API",
        "version": "3.0",
        "storage": "PostgreSQL via SQLAlchemy ORM" if DATABASE_URL else "In-Memory (no DB)",
        "docs":    "/docs",
    }


@app.get("/health", tags=["info"], summary="Health check")
def health():
    return {"status": "ok"}


@app.get("/stats", tags=["info"], summary="Task statistics")
def stats(svc: TaskService = Depends(get_service)):
    return svc.stats()


# ── Run locally (no Docker) ───────────────────────────────────
# uvicorn main:app --reload
# → http://localhost:8000/docs
