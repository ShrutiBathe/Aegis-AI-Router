"""
app/main.py

Real application entrypoint. main_test.py (pre-existing) only mounted
four routers with no DB startup/shutdown handling and no orchestrator;
this supersedes it for actually running the integrated system. Run
with:

    uvicorn app.main:app --reload

from the directory *containing* app/ (i.e. app.<module> must resolve),
matching the import convention already used throughout main_test.py
and payments/router.py.
"""

from dotenv import load_dotenv

load_dotenv()
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.analytics.router import router as analytics_router
from app.database.session import init_sync_db
# Import stub_models so its tables register on the shared sync Base
# before init_sync_db() runs — see that file's docstring for why they
# exist and when to delete them.
from app.database import stub_models  # noqa: F401
from app.execution.router import router as execution_router
from app.history.database import Base as HistoryBase, engine as async_engine
from app.history.router import router as history_router
from app.orchestrator.router import router as orchestrator_router
from app.payments.router import router as payment_router, wallet_router
from app.reputation.db import init_db as init_reputation_db
from app.reputation.router import router as reputation_router
from app.self_healing.router import router as self_healing_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Sync side: Payment (+ stub users/agents/tasks tables it depends on).
    # Execution keeps its own separate sync engine/table creation in
    # execution/router.py (untouched) since it's mounted standalone.
    init_sync_db()

    # Async side: History + Reputation share one engine (app.database.async_db)
    # but each keeps its own declarative Base, so each creates its own table.
    async with async_engine.begin() as conn:
        await conn.run_sync(HistoryBase.metadata.create_all)
    await init_reputation_db()

    yield


app = FastAPI(title="Aegis AI Router — Team B2", lifespan=lifespan)

# Standalone module routers (each independently testable, per their own READMEs)
app.include_router(payment_router)
app.include_router(wallet_router)
app.include_router(execution_router)
app.include_router(self_healing_router)
app.include_router(reputation_router)
app.include_router(history_router)
app.include_router(analytics_router)

# The integrated master workflow (rule #12)
app.include_router(orchestrator_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "aegis-ai-router"}
