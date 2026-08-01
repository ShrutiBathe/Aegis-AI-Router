"""
service.py
----------
SelfHealingService: the single entry point the rest of B2 (Execution,
History, Analytics) calls into. It wires together:

    provider_interface  (AI Integrations module clients)
          -> retry.Retry            (per-attempt backoff)
          -> circuit_breaker        (per-provider open/closed state)
          -> failover.FailoverExecutor (switches provider on failure)

and emits structured events so the History and Analytics modules can log
executions without this module needing to know their internals (simple
callback hooks, wired in __init__).
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Optional

from .circuit_breaker import CircuitBreakerConfig, CircuitBreakerRegistry, circuit_breaker_registry
from .failover import AllProvidersFailedError, FailoverExecutor, FailoverResult, ReputationScorer
from .provider_interface import AIProviderResponse, provider_registry
from .retry import RetryConfig

logger = logging.getLogger("self_healing.service")

# Signature: (event: dict) -> None   (sync or fire-and-forget; kept simple/non-blocking)
EventHook = Callable[[dict[str, Any]], None]


@dataclass
class TaskRequest:
    prompt: str
    preferred_providers: list[str] | None = None  # e.g. from the Router/ranking module
    extra_params: dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class TaskResult:
    request_id: str
    success: bool
    response: AIProviderResponse | None
    winning_provider: str | None
    attempted_providers: list[str]
    total_duration_ms: float
    error: str | None = None


DEFAULT_PROVIDER_CHAIN = ["openai", "gemini", "claude", "groq", "ollama"]


class SelfHealingService:
    def __init__(
        self,
        retry_config: RetryConfig | None = None,
        circuit_breaker_config: CircuitBreakerConfig | None = None,
        reputation_scorer: Optional[ReputationScorer] = None,
        breaker_registry: CircuitBreakerRegistry | None = None,
        on_event: EventHook | None = None,
    ):
        self._retry_config = retry_config or RetryConfig()
        self._breakers = breaker_registry or circuit_breaker_registry
        if circuit_breaker_config:
            self._breakers = CircuitBreakerRegistry(circuit_breaker_config)
        self._failover = FailoverExecutor(
            circuit_breaker_registry=self._breakers,
            retry_config=self._retry_config,
            reputation_scorer=reputation_scorer,
        )
        # Fire-and-forget hook for History/Analytics modules. Kept generic so
        # this module has zero import-time dependency on either.
        self._on_event = on_event or (lambda event: None)

    async def _call_provider(self, provider_name: str, prompt: str, **kwargs: Any) -> AIProviderResponse:
        client = provider_registry.get_client(provider_name)
        return await client.execute(prompt, **kwargs)

    def _emit(self, event_type: str, **payload: Any) -> None:
        try:
            self._on_event({"event": event_type, "timestamp": time.time(), **payload})
        except Exception:
            logger.exception("event hook raised (event=%s) - ignoring", event_type)

    async def execute_task(self, task: TaskRequest) -> TaskResult:
        candidates = task.preferred_providers or DEFAULT_PROVIDER_CHAIN
        start = time.perf_counter()

        self._emit("task_started", request_id=task.request_id, candidates=candidates)

        async def call_provider(provider_name: str) -> AIProviderResponse:
            return await self._call_provider(provider_name, task.prompt, **task.extra_params)

        try:
            result: FailoverResult = await self._failover.execute(candidates, call_provider)
            duration_ms = (time.perf_counter() - start) * 1000

            self._emit(
                "task_succeeded",
                request_id=task.request_id,
                winning_provider=result.winning_provider,
                attempts=[a.__dict__ for a in result.attempts],
                duration_ms=duration_ms,
            )

            return TaskResult(
                request_id=task.request_id,
                success=True,
                response=result.response,
                winning_provider=result.winning_provider,
                attempted_providers=[a.provider for a in result.attempts],
                total_duration_ms=duration_ms,
            )

        except AllProvidersFailedError as exc:
            duration_ms = (time.perf_counter() - start) * 1000
            self._emit(
                "task_failed",
                request_id=task.request_id,
                attempted=exc.attempted,
                errors=exc.errors,
                duration_ms=duration_ms,
            )
            return TaskResult(
                request_id=task.request_id,
                success=False,
                response=None,
                winning_provider=None,
                attempted_providers=exc.attempted,
                total_duration_ms=duration_ms,
                error=str(exc),
            )

    def circuit_breaker_status(self) -> list[dict[str, Any]]:
        return [s.__dict__ for s in self._breakers.all_status()]

    def reset_circuit_breaker(self, provider_name: str | None = None) -> None:
        if provider_name:
            self._breakers.reset(provider_name)
        else:
            self._breakers.reset_all()


# Module-level singleton used by the FastAPI router. Other modules (History,
# Analytics) can subscribe by constructing their own SelfHealingService with
# an `on_event` callback, or by wrapping this instance's `_emit` externally.
self_healing_service = SelfHealingService()
