"""
app/database/session.py

Sync engine/session for modules built on sync SQLAlchemy (Payment).
`payments/router.py` already does

    from app.database.session import get_db

so this just has to exist. Uses the same DATABASE_URL env var as the
async side (app/database/async_db.py) but with a sync driver, so both
halves of the app point at the same physical database by default.
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .base import Base

# Sync driver (psycopg2) by default; SQLite fallback for zero-setup local dev.
SYNC_DATABASE_URL = os.getenv(
    "SYNC_DATABASE_URL",
    os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/aegis_router")
    .replace("+asyncpg", "+psycopg2"),
)

_connect_args = {"check_same_thread": False} if SYNC_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(SYNC_DATABASE_URL, connect_args=_connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db():
    """FastAPI dependency — yields a request-scoped sync Session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_sync_db() -> None:
    """Create tables for every model registered on this Base. Call once at
    startup. Prefer Alembic migrations in production."""
    Base.metadata.create_all(bind=engine)
