"""SQLAlchemy engine and transaction boundaries."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def create_engine_from_url(database_url: str, *, echo: bool = False) -> Engine:
    """Create a PostgreSQL or SQLite engine with safe local defaults."""
    connect_args: dict[str, Any] = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(database_url, echo=echo, future=True, connect_args=connect_args)


class Database:
    """Unit-of-work helper; callers explicitly own migration lifecycle."""

    def __init__(self, database_url: str, *, echo: bool = False) -> None:
        self.engine = create_engine_from_url(database_url, echo=echo)
        self.session_factory = sessionmaker(self.engine, expire_on_commit=False)

    @contextmanager
    def session(self) -> Iterator[Session]:
        """Commit on success and rollback on all failures."""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def dispose(self) -> None:
        """Release pooled connections."""
        self.engine.dispose()
