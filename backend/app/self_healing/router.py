"""
router.py
---------
FastAPI router for the Self-Healing module. Mount this in the main app with:

    from self_healing.router import router as self_healing_router
    app.include_router(self_healing_router)
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .service import SelfHealingService, TaskRequest, self_healing_service

router = APIRouter(prefix="/self-healing", tags=["self-healing"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ExecuteRequest(BaseModel):
    prompt: str = Field(..., description="The prompt/task payload to send to a provider")
    preferred_providers: Optional[list[str]] = Field(
        default=None,
        description="Ordered candidate providers, e.g. from the routing/reputation module. "
                    "Defaults to the module's standard fallback chain.",
    )
    extra_params: dict[str, Any] = Field(default_factory=dict)


class ProviderResponseModel(BaseModel):
    provider: str
    content: str
    latency_ms: float
    metadata: dict[str, Any]


class ExecuteResponse(BaseModel):
    request_id: str
    success: bool
    winning_provider: Optional[str]
    attempted_providers: list[str]
    total_duration_ms: float
    response: Optional[ProviderResponseModel]
    error: Optional[str]


class CircuitBreakerStatusModel(BaseModel):
    provider: str
    state: str
    consecutive_failures: int
    consecutive_successes: int
    opened_at: Optional[float]
    half_open_calls_in_flight: int


class ResetRequest(BaseModel):
    provider: Optional[str] = Field(
        default=None, description="Provider to reset. Omit to reset all breakers."
    )


# ---------------------------------------------------------------------------
# Dependency accessor (kept simple; swap for FastAPI Depends + DI container
# if the rest of the app uses one)
# ---------------------------------------------------------------------------

def get_service() -> SelfHealingService:
    return self_healing_service


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/execute", response_model=ExecuteResponse)
async def execute(payload: ExecuteRequest) -> ExecuteResponse:
    """
    Execute a task with full self-healing: retry -> circuit breaker -> failover.
    Called by the Execution module when it wants failure-tolerant provider calls.
    """
    service = get_service()
    task = TaskRequest(
        prompt=payload.prompt,
        preferred_providers=payload.preferred_providers,
        extra_params=payload.extra_params,
    )
    result = await service.execute_task(task)

    return ExecuteResponse(
        request_id=result.request_id,
        success=result.success,
        winning_provider=result.winning_provider,
        attempted_providers=result.attempted_providers,
        total_duration_ms=result.total_duration_ms,
        response=(
            ProviderResponseModel(
                provider=result.response.provider,
                content=result.response.content,
                latency_ms=result.response.latency_ms,
                metadata=result.response.metadata,
            )
            if result.response
            else None
        ),
        error=result.error,
    )


@router.get("/circuit-breakers", response_model=list[CircuitBreakerStatusModel])
async def get_circuit_breakers() -> list[CircuitBreakerStatusModel]:
    """Current state of every provider's circuit breaker (closed/open/half-open)."""
    service = get_service()
    return [CircuitBreakerStatusModel(**s) for s in service.circuit_breaker_status()]


@router.post("/circuit-breakers/reset")
async def reset_circuit_breaker(payload: ResetRequest) -> dict[str, str]:
    """Manually force a breaker (or all breakers) back to CLOSED. Admin/ops use."""
    service = get_service()
    try:
        service.reset_circuit_breaker(payload.provider)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"status": "reset", "provider": payload.provider or "all"}


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "module": "self-healing"}
