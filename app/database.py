"""SQLAlchemy engine and request-scoped database session helpers."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """Base class for database entities."""


def _connect_args(database_url: str) -> dict[str, bool]:
    return {"check_same_thread": False} if database_url.startswith("sqlite") else {}


engine = create_engine(
    settings.database_url, connect_args=_connect_args(settings.database_url)
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and always release it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
