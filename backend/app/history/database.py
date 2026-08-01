"""
Database session handling for the History module.

INTEGRATION UPDATE: this used to create its own engine pointed at its
own default database. It now re-exports the app-wide shared async
engine/session from app.database.async_db, per this file's own
original NOTE ("delete this file and import Base + get_db from that
shared module instead"). `Base` stays defined here (History's model
table doesn't need to share a declarative registry with anything
else) — only the *connection* is now shared.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.database.async_db import AsyncSessionLocal, engine  # noqa: F401 (re-exported)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
