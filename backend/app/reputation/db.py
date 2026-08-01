"""
db.py — Async SQLAlchemy engine/session setup for the Reputation module.

INTEGRATION UPDATE: this used to default to a *different* database
(`aegis_reputation`) than History's default (`aegis_router`) — in a
real deployment that's an easy way to end up with Reputation silently
writing to a database nothing else reads from. It now shares the
app-wide async engine from app.database.async_db, same as History and
Analytics, per this file's own original comment ("replace DATABASE_URL
with the shared connection string ... so they all share one database").
`Base`/`init_db` stay as-is — Reputation's table doesn't need to share
a declarative registry, only the connection.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.async_db import AsyncSessionLocal, engine  # noqa: F401 (re-exported)

from .models import Base


async def init_db() -> None:
    """Create tables on startup. Prefer Alembic migrations in production."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """FastAPI dependency — yields a request-scoped AsyncSession."""
    async with AsyncSessionLocal() as session:
        yield session
