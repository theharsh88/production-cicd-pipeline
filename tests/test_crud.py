from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import crud
from app.database import Base
from app.schemas import TaskCreate, TaskUpdate


def test_crud_persists_and_removes_task() -> None:
    engine = create_engine("sqlite://")
    session_factory = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    try:
        with session_factory() as db:
            created = crud.create_task(
                db,
                TaskCreate(
                    title="Persist me", description="database test", priority=4
                ),
            )
            assert crud.get_task(db, created.id) is not None
            assert [task.id for task in crud.list_tasks(db)] == [created.id]
            changed = crud.update_task(db, created, TaskUpdate(completed=True))
            assert changed.completed is True
            crud.delete_task(db, changed)
            assert crud.get_task(db, created.id) is None
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
