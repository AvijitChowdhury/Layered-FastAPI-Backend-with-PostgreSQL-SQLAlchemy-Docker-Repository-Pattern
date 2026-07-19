# ============================================================
# app/service.py — Business logic
#
# Sits between routes (HTTP) and repository (storage).
# Owns all business rules — validation, computed fields, etc.
# Doesn't know about HTTP status codes or SQL.
# ============================================================

from typing import List, Optional
from app.repository import TaskRepository
from app.models import Task, TaskCreate, TaskUpdate


class TaskService:

    def __init__(self, repo: TaskRepository):
        self._repo = repo   # injected — could be SQLAlchemy or in-memory

    def list_tasks(self) -> List[Task]:
        return self._repo.get_all()

    def get_task(self, task_id: int) -> Optional[Task]:
        return self._repo.get_by_id(task_id)

    def create_task(self, data: TaskCreate) -> Task:
        # Business rule: title must not be blank
        if not data.title or not data.title.strip():
            raise ValueError("title must not be empty")
        return self._repo.create(data)

    def update_task(self, task_id: int, data: TaskUpdate) -> Optional[Task]:
        # Business rule: at least one field must be provided
        if data.title is None and data.done is None:
            raise ValueError("send at least one of: title, done")
        if data.title is not None and not data.title.strip():
            raise ValueError("title must not be empty")
        return self._repo.update(task_id, data)

    def delete_task(self, task_id: int) -> bool:
        return self._repo.delete(task_id)

    def stats(self) -> dict:
        tasks = self._repo.get_all()
        done  = sum(1 for t in tasks if t.done)
        return {
            "total": len(tasks),
            "done":  done,
            "open":  len(tasks) - done,
        }
