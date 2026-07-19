# ============================================================
# app/models.py
#
# This file has TWO kinds of models — a very important distinction:
#
# 1. SQLAlchemy ORM Model (TaskORM)
#    ─────────────────────────────
#    Represents a ROW in the database table.
#    SQLAlchemy uses it to generate SQL and map results.
#    Lives in the database layer.
#
# 2. Pydantic Schemas (Task, TaskCreate, TaskUpdate)
#    ─────────────────────────────────────────────────
#    Represent the shape of JSON coming IN and going OUT.
#    FastAPI uses them to validate requests and serialize responses.
#    Live in the HTTP layer.
#
# WHY TWO SEPARATE MODELS?
# Your database row and your API response don't have to be identical.
# Example: the DB row might have created_at, updated_at, password_hash —
# fields you never want to expose in the API. Keeping them separate
# gives you full control over what the client sees.
# ============================================================

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel
from typing import Optional


# ── SQLAlchemy ORM ────────────────────────────────────────────

class Base(DeclarativeBase):
    """
    Base class for all ORM models.
    Every class that inherits from Base becomes a database table.
    SQLAlchemy reads the class attributes and maps them to columns.
    """
    pass


class TaskORM(Base):
    """
    ORM model — maps to the 'tasks' table in PostgreSQL.

    When SQLAlchemy sees this class it knows:
      • table name  = "tasks"
      • columns     = id, title, done
      • primary key = id (auto-increment)

    You never write CREATE TABLE SQL by hand —
    Base.metadata.create_all(engine) generates and runs it.
    """
    __tablename__ = "tasks"                         # table name in Postgres

    id    = Column(Integer, primary_key=True, index=True)
    #              ↑                           ↑
    #         Python int               adds a DB index on this column
    #         mapped to SERIAL          (fast lookups by id)

    title = Column(String(500), nullable=False)
    #              ↑             ↑
    #         VARCHAR(500)    NOT NULL constraint

    done  = Column(Boolean, nullable=False, default=False)
    #                                       ↑
    #                               DEFAULT FALSE in SQL


# ── Pydantic Schemas ──────────────────────────────────────────

class Task(BaseModel):
    """
    What the API sends BACK to clients.
    Every field here appears in the JSON response.
    model_config tells Pydantic: "you can build me from an ORM object,
    not just a dict". This is what lets us do Task.model_validate(orm_obj).
    """
    id:    int
    title: str
    done:  bool

    model_config = {"from_attributes": True}
    # from_attributes = True means:
    #   Task.model_validate(task_orm_object) works
    #   Pydantic reads task_orm.id, task_orm.title, task_orm.done


class TaskCreate(BaseModel):
    """What the client sends to CREATE a task (POST /tasks/)."""
    title: str      # required — must be a non-empty string


class TaskUpdate(BaseModel):
    """What the client sends to UPDATE a task (PUT /tasks/{id}).
    Both Optional — client can send one or both fields."""
    title: Optional[str]  = None
    done:  Optional[bool] = None
