# ============================================================
# app/routes.py — HTTP endpoints
#
# Maps URLs + HTTP methods to Python functions.
# Calls service methods, converts errors to HTTP responses.
# Unchanged from previous version — same paths, same status codes.
# ============================================================

from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.models import Task, TaskCreate, TaskUpdate
from app.service import TaskService
from app.dependencies import get_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=List[Task], summary="List all tasks")
def list_tasks(svc: TaskService = Depends(get_service)):
    return svc.list_tasks()


@router.get("/{task_id}", response_model=Task, summary="Get one task")
def get_task(task_id: int, svc: TaskService = Depends(get_service)):
    task = svc.get_task(task_id)
    if task is None:
        raise HTTPException(404, detail=f"Task {task_id} not found")
    return task


@router.post("/", response_model=Task, status_code=201, summary="Create a task")
def create_task(body: TaskCreate, svc: TaskService = Depends(get_service)):
    try:
        return svc.create_task(body)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.put("/{task_id}", response_model=Task, summary="Update a task")
def update_task(task_id: int, body: TaskUpdate, svc: TaskService = Depends(get_service)):
    try:
        task = svc.update_task(task_id, body)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    if task is None:
        raise HTTPException(404, detail=f"Task {task_id} not found")
    return task


@router.delete("/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int, svc: TaskService = Depends(get_service)):
    if not svc.delete_task(task_id):
        raise HTTPException(404, detail=f"Task {task_id} not found")
