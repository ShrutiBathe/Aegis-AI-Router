"""
service.py — Module 2 (Execution Engine)

Orchestrates the full flow from the architecture diagram:

    Receive Agent -> Validate Request -> Call AI Integration
        -> Receive Response -> Return Response
                              -> (on failure only) enqueue Self-Healing

router.py is the only thing that talks to this class. executor.py and
queue.py stay decoupled from each other and from models.py.
"""
from __future__ import annotations

import logging
import uuid

from sqlalchemy.orm import Session

from .executor import AgentNotSupportedError, Executor
from .models import ExecutionRecord, ExecutionStatus
from .queue import SelfHealingQueue
from .schemas import ExecuteRequest, ExecuteResponse

logger = logging.getLogger("execution_engine.service")

# Extend as new AI Integration Layer adapters are registered with the executor.
SUPPORTED_AGENTS = {"openai", "anthropic", "cohere", "mistral"}


class ValidationError(Exception):
    """Raised when a request fails validation before ever reaching the executor."""


class ExecutionEngineService:
    def __init__(self, executor: Executor, self_healing_queue: SelfHealingQueue) -> None:
        self.executor = executor
        self.self_healing_queue = self_healing_queue

    # ---- Validate Request ---------------------------------------------------
    def _validate(self, request: ExecuteRequest) -> None:
        agent_key = request.agent.lower()
        if agent_key not in SUPPORTED_AGENTS:
            raise ValidationError(
                f"Unknown agent '{request.agent}'. Supported agents: {sorted(SUPPORTED_AGENTS)}"
            )
        if not self.executor.supports(request.agent):
            raise ValidationError(
                f"Agent '{request.agent}' is not currently wired to an AI Integration client"
            )
        if len(request.prompt) > 8000:
            raise ValidationError("prompt exceeds maximum length of 8000 characters")

    # ---- Full flow: Receive Agent -> ... -> Return Response ------------------
    async def run(self, request: ExecuteRequest, db: Session) -> ExecuteResponse:
        # Idempotency: if the caller replays a request_id that already
        # succeeded, return the cached result instead of re-executing.
        if request.request_id:
            existing = db.get(ExecutionRecord, request.request_id)
            if existing is not None and existing.status == ExecutionStatus.SUCCESS:
                logger.info("idempotent replay for request_id=%s", request.request_id)
                return ExecuteResponse.model_validate(existing)

        record = ExecutionRecord(
            id=request.request_id or str(uuid.uuid4()),
            agent=request.agent,
            prompt=request.prompt,
            status=ExecutionStatus.PENDING,
        )
        record = db.merge(record)
        db.commit()
        db.refresh(record)

        try:
            self._validate(request)
        except ValidationError as exc:
            record.status = ExecutionStatus.FAILED
            record.error = str(exc)
            db.commit()
            db.refresh(record)
            return ExecuteResponse.model_validate(record)

        try:
            result = await self.executor.execute(request.agent, request.prompt, request.params)
        except AgentNotSupportedError as exc:
            record.status = ExecutionStatus.FAILED
            record.error = str(exc)
            db.commit()
            db.refresh(record)
            return ExecuteResponse.model_validate(record)

        record.latency_ms = result.latency_ms
        record.retries = max(result.attempts - 1, 0)

        if result.success:
            record.status = ExecutionStatus.SUCCESS
            record.response = result.response
            record.error = None
        else:
            record.status = ExecutionStatus.FAILED
            record.error = result.error
            # Only on failure, per the diagram: hand off to Self-Healing.
            await self.self_healing_queue.enqueue(
                record.id, request.agent, request.prompt, result.error or "unknown error"
            )
            logger.info("execution %s failed after %s attempt(s); enqueued for self-healing", record.id, result.attempts)

        db.commit()
        db.refresh(record)
        return ExecuteResponse.model_validate(record)
