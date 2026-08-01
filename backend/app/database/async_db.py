"""
app/database/async_db.py

Shared async engine/session for the async-ORM modules: History,
Reputation, Analytics. Both `history/database.py` and `reputation/db.py`
previously each rolled their own engine pointed at two *different*
default databases (`aegis_router` vs `aegis_reputation`) — meaning in a
single deployment they'd silently write to different databases unless
someone remembered to override both env vars identically.

Both of those files now just re-export from here (see the "why" notes
in their diffs), so there is exactly one async engine for the whole app.
"""
import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/aegis_router",
)

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
