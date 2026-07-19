# ============================================================
# app/repository.py — Abstract repository interface
#
# This defines the CONTRACT that any storage backend must follow.
# Both InMemoryTaskRepository and SQLAlchemyTaskRepository
# implement every method listed here.
#
# Because routes and service only call these 5 methods,
# swapping storage is just wiring a different implementation.
# ============================================================

from abc import ABC, abstractmethod
from typing import List, Optional
from app.models import Task, TaskCreate, TaskUpdate


class TaskRepository(ABC):

    @abstractmethod
    def get_all(self) -> List[Task]:
        """Return all tasks."""
        ...

    @abstractmethod
    def get_by_id(self, task_id: int) -> Optional[Task]:
        """Return one task by id, or None if not found."""
        ...

    @abstractmethod
    def create(self, data: TaskCreate) -> Task:
        """Persist a new task and return it with its assigned id."""
        ...

    @abstractmethod
    def update(self, task_id: int, data: TaskUpdate) -> Optional[Task]:
        """Update fields. Returns None if task_id doesn't exist."""
        ...

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        """Delete a task. Returns True if deleted, False if not found."""
        ...
