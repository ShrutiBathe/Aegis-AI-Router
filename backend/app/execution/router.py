"""
router.py — Module 2 (Execution Engine)

HTTP surface:
    POST /execute            Receive Agent -> ... -> Return Response
    GET  /execute/{id}        Look up a past execution (used by History/Analytics)

The DB engine and Executor wiring at the bottom of this file are minimal
defaults so Module 2 is runnable standalone. In the full system, the app's
main.py should own the real session factory and register real AI
Integration Layer clients, then override get_db / get_execution_service.
"""
from __future__ import annotations

import logging
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .executor import Executor
from .models import Base, ExecutionRecord
from .queue import InMemorySelfHealingQueue
from .schemas import ExecuteRequest, ExecuteResponse, ExecutionRecordOut
from .service import ExecutionEngineService, ValidationError

logger = logging.getLogger("execution_engine.router")

router = APIRouter(prefix="/execute", tags=["execution-engine"])

# --------------------------------------------------------------------------
# Minimal default wiring — override in the app's real bootstrap (main.py).
# --------------------------------------------------------------------------
_engine = create_engine("sqlite:///./execution_engine.db", connect_args={"check_same_thread": False})
Base.metadata.create_all(_engine)
_SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)


def get_db():
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


@lru_cache
def _service_singleton() -> ExecutionEngineService:
    executor = Executor()
    # Register real AI Integration Layer clients at startup, e.g.:
    #   executor.register_client("openai", OpenAIIntegrationClient(api_key=...))
    #   executor.register_client("anthropic", AnthropicIntegrationClient(api_key=...))
    queue = InMemorySelfHealingQueue()
    return ExecutionEngineService(executor=executor, self_healing_queue=queue)


def get_execution_service() -> ExecutionEngineService:
    return _service_singleton()


@router.post("", response_model=ExecuteResponse, status_code=status.HTTP_200_OK)
async def execute(
    request: ExecuteRequest,
    db: Session = Depends(get_db),
    service: ExecutionEngineService = Depends(get_execution_service),
) -> ExecuteResponse:
    """
    POST /execute
    {
        "agent": "OpenAI",
        "prompt": "Explain AI Routing"
    }
    """
    try:
        return await service.run(request, db)
    except ValidationError as exc:
        # service.run() normally swallows ValidationError and returns a
        # persisted "failed" record instead (so History/Analytics have a
        # full audit trail, including rejected requests). This handler is
        # kept as a safety net in case that behavior ever changes.
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 — never leak internals to the client
        logger.exception("unexpected failure executing agent=%s", request.agent)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="execution engine failure"
        ) from exc


@router.get("/{execution_id}", response_model=ExecutionRecordOut)
def get_execution(execution_id: str, db: Session = Depends(get_db)) -> ExecutionRecordOut:
    record = db.get(ExecutionRecord, execution_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="execution not found")
    return ExecutionRecordOut.model_validate(record)
