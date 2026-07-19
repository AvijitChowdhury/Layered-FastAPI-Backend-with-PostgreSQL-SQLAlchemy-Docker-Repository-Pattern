# ============================================================
# app/dependencies.py — Dependency injection wiring
#
# FastAPI calls get_service() for every request that declares
# `svc: TaskService = Depends(get_service)`.
#
# DECISION LOGIC:
#   DATABASE_URL set (Docker/production) → SQLAlchemyTaskRepository
#   DATABASE_URL not set (local dev)     → InMemoryTaskRepository
#
# The routes and service never know which one is active.
# ============================================================

import os
from sqlalchemy.orm import Session
from fastapi import Depends
from dotenv import load_dotenv

from app.database import get_db, DATABASE_URL
from app.service import TaskService
from app.repository import TaskRepository

load_dotenv()


def get_repo(db: Session = Depends(get_db)) -> TaskRepository:
    """
    Returns the appropriate repository based on environment.

    When DATABASE_URL is set:
      • db is a real Postgres session from get_db()
      • we wrap it in SQLAlchemyTaskRepository

    When DATABASE_URL is not set:
      • db is a SQLite :memory: session (also from get_db())
      • we use InMemoryTaskRepository (no DB needed at all)
    """
    if DATABASE_URL:
        from app.sqlalchemy_repo import SQLAlchemyTaskRepository
        return SQLAlchemyTaskRepository(db)
    else:
        from app.memory_repo import InMemoryTaskRepository
        return InMemoryTaskRepository()


def get_service(repo: TaskRepository = Depends(get_repo)) -> TaskService:
    """Wraps the repository in the service layer."""
    return TaskService(repo)
