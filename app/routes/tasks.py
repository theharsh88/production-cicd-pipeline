"""Task CRUD endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def _task_or_404(db: Session, task_id: int):
    task = crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create(payload: TaskCreate, db: Session = Depends(get_db)) -> TaskRead:
    return crud.create_task(db, payload)


@router.get("", response_model=list[TaskRead])
def read_all(db: Session = Depends(get_db)) -> list[TaskRead]:
    return crud.list_tasks(db)


@router.get("/{task_id}", response_model=TaskRead)
def read_one(task_id: int, db: Session = Depends(get_db)) -> TaskRead:
    return _task_or_404(db, task_id)


@router.put("/{task_id}", response_model=TaskRead)
def update(
    task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)
) -> TaskRead:
    return crud.update_task(db, _task_or_404(db, task_id), payload)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove(task_id: int, db: Session = Depends(get_db)) -> Response:
    crud.delete_task(db, _task_or_404(db, task_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
