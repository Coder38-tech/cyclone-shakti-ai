from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.exceptions import DatabaseError
from app.core.logging_config import get_logger
from app.models.database_models import Base

logger = get_logger("database.connection")


class Database:
    """Wraps SQLAlchemy engine + session factory.

    SQLite by default (dev). Switch to PostgreSQL by setting DATABASE_URL to
    a postgresql+psycopg:// URL; the rest of the codebase remains identical.
    """

    def __init__(self, database_url: Optional[str] = None, echo: bool = False):
        self.settings = get_settings()
        url = database_url or self.settings.database_url
        connect_args = {}
        if url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
        self.engine: Engine = create_engine(url, echo=echo, connect_args=connect_args, future=True)
        self._SessionLocal = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            future=True,
        )

    def create_tables(self) -> None:
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created/verified successfully")
        except Exception as exc:
            logger.exception("Failed to create database tables: %s", exc)
            raise DatabaseError("Failed to initialise database schema") from exc

    def check_available(self) -> bool:
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as exc:
            logger.warning("Database health check failed: %s", exc)
            return False

    def SessionLocal(self) -> Session:
        return self._SessionLocal()

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


_db: Optional[Database] = None


def get_database(database_url: Optional[str] = None) -> Database:
    global _db
    if _db is None:
        _db = Database(database_url=database_url)
        _db.create_tables()
    return _db


def reset_database() -> None:
    global _db
    _db = None


def get_db_session() -> Generator[Session, None, None]:
    """FastAPI dependency — yields a per-request session."""
    db = get_database()
    session = db.SessionLocal()
    try:
        yield session
    finally:
        session.close()
