"""
app/orchestrator/router.py

Per rule #10: dependency injection lives only here; OrchestratorService
(service.py) holds all the business logic/sequencing, this file just
wires request -> service -> response and translates the two expected
"stop immediately" error paths into HTTP responses.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.database.async_db import get_async_db
from app.database.session import get_db as get_sync_db

from .schemas import TaskRunRequest, TaskRunResponse
from .service import DuplicateTaskRequest, OrchestratorService, PaymentAuthorizationFailed

router = APIRouter(prefix="/tasks", tags=["orchestrator"])


def get_orchestrator(
    payment_db: Session = Depends(get_sync_db),
    async_db: AsyncSession = Depends(get_async_db),
) -> OrchestratorService:
    return OrchestratorService(payment_db=payment_db, async_db=async_db)


@router.post("/run", response_model=TaskRunResponse)
async def run_task(
    payload: TaskRunRequest,
    orchestrator: OrchestratorService = Depends(get_orchestrator),
) -> TaskRunResponse:
    """
    The full Aegis AI Router pipeline for a single task:
    Payment authorize -> Self-Healing (Execution + AI Integrations +
    retry/failover) -> Payment capture/refund -> History -> Reputation
    -> Analytics -> response.
    """
    try:
        return await orchestrator.run(payload)
    except PaymentAuthorizationFailed as exc:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=exc.detail
        ) from exc
    except DuplicateTaskRequest as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=exc.detail
        ) from exc
