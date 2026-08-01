"""
failover.py
-----------
Provider switching: given an ordered list of candidate providers, try each
one (through retry + circuit breaker) until one succeeds.

Ordering defaults to the order passed in, but a `reputation_scorer` callable
can be injected (wired to the Reputation module) to rank providers by trust
score before attempting failover, so healthier/higher-rated providers are
tried first.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Optional

from .circuit_breaker import CircuitBreaker, CircuitBreakerOpenError, CircuitBreakerRegistry
from .provider_interface import AIProviderError, AIProviderResponse
from .retry import Retry, RetryAttemptLog, RetryConfig, RetryExhaustedError

logger = logging.getLogger("self_healing.failover")

# Signature: (provider_name: str) -> float   (higher = more trusted)
ReputationScorer = Callable[[str], float]


class AllProvidersFailedError(Exception):
    """Raised when every candidate provider in the failover chain has failed."""

    def __init__(self, attempted: list[str], errors: dict[str, str]):
        self.attempted = attempted
        self.errors = errors
        super().__init__(
            f"all providers failed: {', '.join(f'{p} ({errors.get(p)})' for p in attempted)}"
        )


@dataclass
class ProviderAttemptResult:
    provider: str
    succeeded: bool
    error: str | None
    retry_log: list[RetryAttemptLog] = field(default_factory=list)


@dataclass
class FailoverResult:
    response: AIProviderResponse
    winning_provider: str
    attempts: list[ProviderAttemptResult]


class FailoverExecutor:
    def __init__(
        self,
        circuit_breaker_registry: CircuitBreakerRegistry,
        retry_config: RetryConfig | None = None,
        reputation_scorer: Optional[ReputationScorer] = None,
    ):
        self._breakers = circuit_breaker_registry
        self._retry_config = retry_config or RetryConfig()
        self._reputation_scorer = reputation_scorer

    def _order_providers(self, candidates: list[str]) -> list[str]:
        if not self._reputation_scorer:
            return list(candidates)
        try:
            return sorted(candidates, key=self._reputation_scorer, reverse=True)
        except Exception:
            logger.warning("reputation_scorer failed, falling back to given order")
            return list(candidates)

    async def execute(
        self,
        candidates: list[str],
        call_provider: Callable[[str], Awaitable[AIProviderResponse]],
    ) -> FailoverResult:
        """
        `call_provider(provider_name)` should perform the actual provider
        call (e.g. `provider_registry.get_client(name).execute(prompt)`).

        Tries providers in ranked order. Each attempt is wrapped in that
        provider's circuit breaker + retry policy. On success, returns
        immediately. If every provider fails/rejects, raises
        AllProvidersFailedError.
        """
        ordered = self._order_providers(candidates)
        attempts: list[ProviderAttemptResult] = []
        errors: dict[str, str] = {}

        for provider in ordered:
            breaker: CircuitBreaker = self._breakers.get(provider)
            retry = Retry(self._retry_config)

            async def _attempt() -> AIProviderResponse:
                result, _log = await retry.run(call_provider, provider, provider_name=provider)
                return result

            try:
                response = await breaker.call(_attempt)
                attempts.append(ProviderAttemptResult(provider=provider, succeeded=True, error=None))
                logger.info("failover succeeded on provider=%s (chain=%s)", provider, ordered)
                return FailoverResult(response=response, winning_provider=provider, attempts=attempts)

            except CircuitBreakerOpenError as exc:
                errors[provider] = f"circuit_open (retry_after={exc.retry_after_seconds:.1f}s)"
                attempts.append(ProviderAttemptResult(provider=provider, succeeded=False, error=errors[provider]))
                logger.warning("provider=%s skipped: circuit open, switching to next candidate", provider)
                continue

            except RetryExhaustedError as exc:
                errors[provider] = str(exc.last_error)
                attempts.append(ProviderAttemptResult(provider=provider, succeeded=False, error=errors[provider]))
                logger.warning("provider=%s exhausted retries, switching to next candidate", provider)
                continue

            except AIProviderError as exc:
                errors[provider] = str(exc)
                attempts.append(ProviderAttemptResult(provider=provider, succeeded=False, error=errors[provider]))
                if not exc.retryable:
                    logger.warning("provider=%s non-retryable, switching to next candidate", provider)
                continue

        raise AllProvidersFailedError(attempted=ordered, errors=errors)
