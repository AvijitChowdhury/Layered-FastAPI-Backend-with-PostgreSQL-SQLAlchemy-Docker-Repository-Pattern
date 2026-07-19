# ============================================================
# app/sqlalchemy_repo.py — SQLAlchemy ORM repository
#
# This replaces the raw psycopg2 postgres_repo.py.
# Instead of writing SQL strings by hand, we use SQLAlchemy's
# ORM — Python objects and method calls that SQLAlchemy
# translates into SQL automatically.
#
# RAW SQL (old way, postgres_repo.py):
#   cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
#   row = cur.fetchone()
#
# SQLALCHEMY ORM (new way, this file):
#   task = db.query(TaskORM).filter(TaskORM.id == task_id).first()
#
# BENEFITS OF ORM:
#   • No raw SQL strings — fewer typos, auto-escaping (no injection)
#   • IDE autocomplete on column names
#   • Works with multiple databases (switch Postgres → SQLite → MySQL
#     by changing one URL, no code changes)
#   • Schema managed in Python (no separate .sql files needed)
#
# HOW SQLALCHEMY TRANSLATES ORM TO SQL:
#   db.query(TaskORM).all()
#     → SELECT id, title, done FROM tasks
#
#   db.query(TaskORM).filter(TaskORM.id == 1).first()
#     → SELECT id, title, done FROM tasks WHERE id = 1 LIMIT 1
#
#   db.add(TaskORM(title="Buy milk", done=False)); db.commit()
#     → INSERT INTO tasks (title, done) VALUES ('Buy milk', false)
#
#   task.title = "Updated"; db.commit()
#     → UPDATE tasks SET title='Updated' WHERE id = 1
#
#   db.delete(task); db.commit()
#     → DELETE FROM tasks WHERE id = 1
# ============================================================

from typing import List, Optional
from sqlalchemy.orm import Session

from app.repository import TaskRepository
from app.models import Task, TaskCreate, TaskUpdate, TaskORM


class SQLAlchemyTaskRepository(TaskRepository):
    """
    PostgreSQL repository using SQLAlchemy ORM.
    Receives a Session from FastAPI's dependency injection
    (injected via Depends(get_db) in dependencies.py).
    """

    def __init__(self, db: Session):
        # db is a SQLAlchemy Session — our "database handle"
        # It stays open for the duration of one HTTP request
        self._db = db

    # ── private helper ────────────────────────────────────────

    def _to_schema(self, orm_obj: TaskORM) -> Task:
        """
        Convert a SQLAlchemy ORM object → Pydantic Task schema.
        model_validate reads attributes from the ORM object directly
        (this works because we set model_config = {"from_attributes": True}
        in the Task schema).
        """
        return Task.model_validate(orm_obj)

    # ── interface implementation ──────────────────────────────

    def get_all(self) -> List[Task]:
        """
        ORM:  db.query(TaskORM).order_by(TaskORM.id).all()
        SQL:  SELECT id, title, done FROM tasks ORDER BY id
        """
        rows = self._db.query(TaskORM).order_by(TaskORM.id).all()
        return [self._to_schema(r) for r in rows]

    def get_by_id(self, task_id: int) -> Optional[Task]:
        """
        ORM:  db.query(TaskORM).filter(TaskORM.id == task_id).first()
        SQL:  SELECT id, title, done FROM tasks WHERE id = ? LIMIT 1
        Returns None if not found (same as fetchone() returning None).
        """
        row = self._db.query(TaskORM).filter(TaskORM.id == task_id).first()
        return self._to_schema(row) if row else None

    def create(self, data: TaskCreate) -> Task:
        """
        ORM:  db.add(new_task); db.commit(); db.refresh(new_task)
        SQL:  INSERT INTO tasks (title, done) VALUES (?, false)
              then SELECT the row back to get the auto-assigned id

        db.refresh(new_task) syncs the ORM object with what's in the DB
        (this is how we get the auto-assigned id back after INSERT).
        """
        new_task = TaskORM(
            title=data.title.strip(),
            done=False,
        )
        self._db.add(new_task)       # stage the INSERT
        self._db.commit()            # execute + commit transaction
        self._db.refresh(new_task)   # reload from DB (gets auto-assigned id)
        return self._to_schema(new_task)

    def update(self, task_id: int, data: TaskUpdate) -> Optional[Task]:
        """
        ORM:  find the row, mutate its attributes, commit
        SQL:  UPDATE tasks SET title=?, done=? WHERE id=?

        SQLAlchemy tracks changes to ORM objects automatically.
        When you set task.title = "new value", SQLAlchemy marks
        the object as "dirty" and includes it in the next commit.
        """
        task = self._db.query(TaskORM).filter(TaskORM.id == task_id).first()
        if task is None:
            return None

        # Only update fields the client actually sent (not None)
        if data.title is not None:
            task.title = data.title.strip()
        if data.done is not None:
            task.done = data.done

        self._db.commit()        # runs: UPDATE tasks SET ... WHERE id = task_id
        self._db.refresh(task)   # sync object with DB state after update
        return self._to_schema(task)

    def delete(self, task_id: int) -> bool:
        """
        ORM:  db.delete(task); db.commit()
        SQL:  DELETE FROM tasks WHERE id = ?

        Returns True if deleted, False if task didn't exist.
        """
        task = self._db.query(TaskORM).filter(TaskORM.id == task_id).first()
        if task is None:
            return False

        self._db.delete(task)    # stage the DELETE
        self._db.commit()        # execute + commit
        return True
