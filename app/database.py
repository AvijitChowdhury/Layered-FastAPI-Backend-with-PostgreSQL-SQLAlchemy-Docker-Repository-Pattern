# ============================================================
# app/database.py — SQLAlchemy engine and session factory
#
# This file sets up the connection to PostgreSQL via SQLAlchemy.
#
# KEY CONCEPTS
# ─────────────────────────────────────────────────────────────
# Engine
#   The engine is SQLAlchemy's connection to your database.
#   It manages a pool of TCP connections to Postgres so you
#   don't have to open/close a new connection for every query.
#   Think of it as the "database driver" wrapper.
#
# Session
#   A session is a unit of work. You use a session to:
#     • query:  session.query(TaskORM).all()
#     • add:    session.add(new_task)
#     • delete: session.delete(task)
#     • save:   session.commit()
#   At the end of each request, the session is closed and
#   returned to the pool.
#
# SessionLocal
#   A factory that produces Session objects.
#   We call SessionLocal() once per request, use it, then close it.
#
# FALLBACK LOGIC
# ─────────────────────────────────────────────────────────────
# If DATABASE_URL is not set, we use SQLite (:memory:) so you
# can run the app without Docker for local testing.
# ============================================================

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()   # reads .env file if present

# ── Read connection string ────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # PostgreSQL — used when running with Docker
    # connect_args is not needed for Postgres (only for SQLite)
    engine = create_engine(DATABASE_URL)
else:
    # SQLite in-memory — fallback for local dev without Docker
    # check_same_thread=False is required for SQLite with FastAPI
    # (FastAPI may call the same connection from different threads)
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

# ── Session factory ───────────────────────────────────────────
# autocommit=False  → we control when to commit (explicit is better)
# autoflush=False   → don't auto-sync to DB before every query
# bind=engine       → which database this session talks to
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    FastAPI dependency that yields a database session.

    Usage in a route:
        def my_route(db: Session = Depends(get_db)):
            tasks = db.query(TaskORM).all()

    The 'yield' makes this a context manager:
      1. Session is created and handed to the route
      2. Route runs its logic
      3. 'finally' block always runs — session closes even if an error happened
         (returns the connection to the pool)

    This pattern is called "one session per request".
    """
    db = SessionLocal()
    try:
        yield db          # hand the session to the route function
    finally:
        db.close()        # always close — never leaks connections
