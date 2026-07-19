# ============================================================
# app/memory_repo.py — In-memory repository
#
# Stores tasks in a plain Python list.
# No database, no Docker, no network — pure Python.
#
# WHEN IS THIS USED?
#   • When DATABASE_URL is NOT set in .env
#   • Local development without Docker running
#   • Unit tests (fast, no I/O)
#
# LIMITATION:
#   Data is lost when the process stops.
#   This is intentional — it shows WHY databases exist.
# ============================================================

from typing import List, Optional
from app.repository import TaskRepository
from app.models import Task, TaskCreate, TaskUpdate


class InMemoryTaskRepository(TaskRepository):
    """
    Stores tasks in a Python list in RAM.
    Pre-seeded with 3 example tasks (same as W2).
    """

    def __init__(self):
        # The "database" — a plain Python list of dicts
        self._tasks: List[dict] = [
            {"id": 1, "title": "Buy groceries", "done": False},
            {"id": 2, "title": "Read a book",   "done": True},
            {"id": 3, "title": "Go for a walk", "done": False},
        ]
        # Counter replaces SERIAL/auto-increment from Postgres
        self._next_id: int = 4

    # ── private helpers ───────────────────────────────────────

    def _find(self, task_id: int) -> Optional[dict]:
        """Linear search through list. Fine for small datasets."""
        return next((t for t in self._tasks if t["id"] == task_id), None)

    def _to_schema(self, raw: dict) -> Task:
        """Convert raw dict → Pydantic Task schema."""
        return Task(**raw)

    # ── interface implementation ──────────────────────────────

    def get_all(self) -> List[Task]:
        return [self._to_schema(t) for t in self._tasks]

    def get_by_id(self, task_id: int) -> Optional[Task]:
        raw = self._find(task_id)
        return self._to_schema(raw) if raw else None

    def create(self, data: TaskCreate) -> Task:
        raw = {
            "id":    self._next_id,
            "title": data.title.strip(),
            "done":  False,
        }
        self._tasks.append(raw)
        self._next_id += 1
        return self._to_schema(raw)

    def update(self, task_id: int, data: TaskUpdate) -> Optional[Task]:
        raw = self._find(task_id)
        if raw is None:
            return None
        if data.title is not None:
            raw["title"] = data.title.strip()
        if data.done is not None:
            raw["done"] = data.done
        return self._to_schema(raw)

    def delete(self, task_id: int) -> bool:
        raw = self._find(task_id)
        if raw is None:
            return False
        self._tasks.remove(raw)
        return True
