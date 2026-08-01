"""
app/orchestrator/service.py

The master workflow from the integration spec (rule #12):

    Payment.authorize_payment()
        -> SelfHealingService.execute_task()   [this already IS
           "call AI Integration -> on failure: retry -> switch
           provider -> retry -> exhaust all candidates", see the
           note in execute_task_and_settle() below]
        -> success: capture_payment, History, Reputation, Analytics
        -> failure: refund_payment (only after every provider is
           exhausted), History, Reputation, Analytics

This module calls into the seven existing services; it doesn't
reimplement any of their business logic. The only genuinely new
logic here is the sequencing itself, plus two small adapters the
existing services don't provide on their own:

  - Payment is sync (SQLAlchemy Session); everything else here is
    async. Payment calls are wrapped in run_in_threadpool so they
    don't block the event loop, without touching PaymentService.
  - Payment requires a UUID `agent_id` (there's no Agents/Marketplace
    table in this handoff); provider_to_agent_id() derives a stable
    UUID5 from the provider name so authorize/capture/refund work
    today. Swap for a real agents table lookup once that module exists.
"""
from __future__ import annotations

import logging
import uuid
from decimal import Decimal
from typing import Optional

from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.analytics.service import AnalyticsService
from app.history.models import ExecutionStatus
from app.history.schemas import HistoryCreate
from app.history.service import HistoryService
from app.payments.gateway import MockGateway
from app.payments.service import (
    DuplicatePaymentError,
    InsufficientBalanceError,
    PaymentService,
)
from app.reputation.schemas import ReputationEventIn
from app.reputation.service import ReputationService
from app.self_healing.service import DEFAULT_PROVIDER_CHAIN, SelfHealingService, TaskRequest

from .schemas import PaymentSummary, TaskRunRequest, TaskRunResponse

logger = logging.getLogger("orchestrator.service")

# Fixed namespace so the same provider name always maps to the same
# UUID across requests/restarts. Placeholder until a real Agents table
# (owned by the Marketplace module) exists — see module docstring.
_AGENT_ID_NAMESPACE = uuid.UUID("a9e91500-0000-4000-8000-000000000000")


def provider_to_agent_id(provider_name: str) -> uuid.UUID:
    return uuid.uuid5(_AGENT_ID_NAMESPACE, provider_name.lower().strip())


class PaymentAuthorizationFailed(Exception):
    """Wraps InsufficientBalanceError with the request context the router needs."""

    def __init__(self, request_id: str, detail: str):
        self.request_id = request_id
        self.detail = detail
        super().__init__(detail)


class DuplicateTaskRequest(Exception):
    """Wraps DuplicatePaymentError — the caller reused an idempotency key."""

    def __init__(self, request_id: str, detail: str):
        self.request_id = request_id
        self.detail = detail
        super().__init__(detail)


class OrchestratorService:
    def __init__(self, payment_db: Session, async_db: AsyncSession):
        self.payment_service = PaymentService(db=payment_db, gateway=MockGateway())
        self.reputation_service = ReputationService(async_db)
        self.async_db = async_db

    async def run(self, payload: TaskRunRequest) -> TaskRunResponse:
        request_id = str(uuid.uuid4())
        idempotency_key = payload.idempotency_key or request_id
        candidates = payload.preferred_providers or DEFAULT_PROVIDER_CHAIN
        primary_provider = candidates[0]
        agent_id = provider_to_agent_id(primary_provider)

        # ---- Rule #1: Payment.authorize_payment() before any execution ----
        cost_estimate = self.payment_service.estimate_cost(
            agent_id=agent_id, estimated_tokens=payload.estimated_tokens
        )
        try:
            payment = await run_in_threadpool(
                self.payment_service.authorize_payment,
                user_id=payload.user_id,
                agent_id=agent_id,
                amount=cost_estimate["estimated_cost"],
                idempotency_key=idempotency_key,
                currency=cost_estimate["currency"],
            )
        except InsufficientBalanceError as exc:
            # Stop immediately. Never call any AI provider. Still record the
            # attempt for audit purposes (rule #7: "regardless of success or
            # failure"), with no payment_id since none was created.
            await HistoryService.create(
                self.async_db,
                HistoryCreate(
                    user_id=str(payload.user_id),
                    provider=primary_provider,
                    prompt=payload.prompt,
                    response=None,
                    cost=0.0,
                    time_taken=None,
                    status=ExecutionStatus.FAILURE,
                    request_id=request_id,
                    retries=0,
                    payment_id=None,
                ),
            )
            raise PaymentAuthorizationFailed(request_id, str(exc)) from exc
        except DuplicatePaymentError as exc:
            raise DuplicateTaskRequest(request_id, str(exc)) from exc

        # ---- Rules #2, #4, #5: Execution + AI Integrations + Self-Healing --
        #
        # self_healing.SelfHealingService.execute_task() already implements
        # exactly the flow rule #5 describes: try a provider (via the AI
        # Integrations bridge in app/ai_integrations/registry.py) with
        # retry+circuit-breaker, and on failure switch to the next candidate,
        # continuing until every candidate is exhausted. That's the same
        # unit of work rules #2+#4+#5 describe together, so it's used as-is
        # here rather than re-implemented. execution/service.py's own
        # Executor+Queue flow is left mounted standalone at POST /execute
        # for isolated testing of that module — its fire-and-forget queue
        # hand-off can't feed a result back into this synchronous response,
        # so it isn't part of the orchestrated path.
        healing_service = SelfHealingService()
        task = TaskRequest(
            prompt=payload.prompt,
            preferred_providers=payload.preferred_providers,
            extra_params=payload.extra_params,
            request_id=request_id,
        )
        result = await healing_service.execute_task(task)
        retries = max(len(result.attempted_providers) - 1, 0)

        if result.success:
            # ---- Rule #3: success flow -------------------------------------
            captured = await run_in_threadpool(
                self.payment_service.capture_payment, payment.id
            )
            await self.reputation_service.record_event(
                ReputationEventIn(
                    provider=result.winning_provider,
                    success=True,
                    latency_ms=result.total_duration_ms,
                )
            )
            history_record = await HistoryService.create(
                self.async_db,
                HistoryCreate(
                    user_id=str(payload.user_id),
                    provider=result.winning_provider,
                    prompt=payload.prompt,
                    response=result.response.content if result.response else None,
                    cost=float(captured.amount),
                    time_taken=result.total_duration_ms,
                    status=ExecutionStatus.SUCCESS,
                    request_id=request_id,
                    retries=retries,
                    payment_id=str(captured.id),
                ),
            )
            await AnalyticsService.record_success(
                provider=result.winning_provider,
                cost=float(captured.amount),
                time_taken=result.total_duration_ms,
                retries=retries,
            )
            return TaskRunResponse(
                request_id=request_id,
                success=True,
                provider=result.winning_provider,
                response=result.response.content if result.response else None,
                error=None,
                attempted_providers=result.attempted_providers,
                retries=retries,
                latency_ms=result.total_duration_ms,
                payment=PaymentSummary(
                    id=captured.id,
                    status=captured.status.value,
                    amount=captured.amount,
                    currency=captured.currency,
                ),
                history_id=history_record.id,
            )

        # ---- Rules #4, #5: failure flow — refund only after every ----------
        # candidate provider has been exhausted (guaranteed here: this branch
        # only runs once self_healing.execute_task() has raised
        # AllProvidersFailedError internally and returned success=False).
        refunded = await run_in_threadpool(
            self.payment_service.refund_payment,
            payment.id,
            result.error or "all candidate providers failed",
        )

        # Rule #6: every provider execution updates Reputation. Per-provider
        # latency for a fully-failed chain isn't exposed on TaskResult (only
        # total_duration_ms and the list of attempted provider names), so it
        # is split evenly across attempts as an approximation — see
        # self_healing/service.py's `_emit` for where finer-grained
        # per-attempt data does exist if this needs tightening later.
        per_attempt_latency = result.total_duration_ms / max(len(result.attempted_providers), 1)
        for provider_name in result.attempted_providers:
            await self.reputation_service.record_event(
                ReputationEventIn(
                    provider=provider_name, success=False, latency_ms=per_attempt_latency
                )
            )

        history_record = await HistoryService.create(
            self.async_db,
            HistoryCreate(
                user_id=str(payload.user_id),
                provider=result.attempted_providers[0] if result.attempted_providers else primary_provider,
                prompt=payload.prompt,
                response=None,
                cost=0.0,
                time_taken=result.total_duration_ms,
                status=ExecutionStatus.FAILURE,
                request_id=request_id,
                retries=retries,
                payment_id=str(refunded.id),
            ),
        )
        await AnalyticsService.record_failure(
            provider=result.attempted_providers[0] if result.attempted_providers else None,
            retries=retries,
            error=result.error,
        )
        return TaskRunResponse(
            request_id=request_id,
            success=False,
            provider=None,
            response=None,
            error=result.error,
            attempted_providers=result.attempted_providers,
            retries=retries,
            latency_ms=result.total_duration_ms,
            payment=PaymentSummary(
                id=refunded.id,
                status=refunded.status.value,
                amount=refunded.amount,
                currency=refunded.currency,
            ),
            history_id=history_record.id,
        )
