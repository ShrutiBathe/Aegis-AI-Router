"""
circuit_breaker.py
-------------------
Per-provider circuit breaker: CLOSED -> OPEN -> HALF_OPEN -> CLOSED.

- CLOSED:      calls flow normally; failures are counted in a rolling window.
- OPEN:        calls are rejected immediately (no network call) until the
               recovery timeout elapses.
- HALF_OPEN:   a limited number of trial calls are allowed through; enough
               consecutive successes closes the breaker again, any failure
               re-opens it.

A CircuitBreakerRegistry keeps one breaker instance per provider so state is
shared across all requests, not per-call.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable, TypeVar

logger = logging.getLogger("self_healing.circuit_breaker")

T = TypeVar("T")


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpenError(Exception):
    """Raised when a call is rejected because the circuit is OPEN."""

    def __init__(self, provider: str, retry_after_seconds: float):
        self.provider = provider
        self.retry_after_seconds = retry_after_seconds
        super().__init__(
            f"[{provider}] circuit is OPEN, retry after {retry_after_seconds:.1f}s"
        )


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5          # consecutive failures before opening (in CLOSED)
    recovery_timeout_seconds: float = 30.0  # how long to stay OPEN before trying HALF_OPEN
    half_open_max_calls: int = 1        # trial calls allowed while HALF_OPEN
    success_threshold: int = 2          # consecutive successes in HALF_OPEN needed to close


@dataclass
class CircuitBreakerStatus:
    provider: str
    state: CircuitState
    consecutive_failures: int
    consecutive_successes: int
    opened_at: float | None
    half_open_calls_in_flight: int


class CircuitBreaker:
    def __init__(self, provider_name: str, config: CircuitBreakerConfig | None = None):
        self.provider_name = provider_name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._consecutive_failures = 0
        self._consecutive_successes = 0
        self._opened_at: float | None = None
        self._half_open_calls_in_flight = 0

    @property
    def state(self) -> CircuitState:
        # Lazily transition OPEN -> HALF_OPEN once recovery timeout has passed.
        if self._state == CircuitState.OPEN and self._opened_at is not None:
            elapsed = time.monotonic() - self._opened_at
            if elapsed >= self.config.recovery_timeout_seconds:
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls_in_flight = 0
                self._consecutive_successes = 0
                logger.info("provider=%s circuit CLOSED->HALF_OPEN (recovery timeout elapsed)",
                            self.provider_name)
        return self._state

    def _retry_after(self) -> float:
        if self._opened_at is None:
            return 0.0
        remaining = self.config.recovery_timeout_seconds - (time.monotonic() - self._opened_at)
        return max(0.0, remaining)

    def _on_success(self) -> None:
        if self.state == CircuitState.HALF_OPEN:
            self._consecutive_successes += 1
            self._half_open_calls_in_flight = max(0, self._half_open_calls_in_flight - 1)
            if self._consecutive_successes >= self.config.success_threshold:
                self._close()
        else:
            self._consecutive_failures = 0
            self._consecutive_successes += 1

    def _on_failure(self) -> None:
        if self.state == CircuitState.HALF_OPEN:
            self._half_open_calls_in_flight = max(0, self._half_open_calls_in_flight - 1)
            self._open()
            return
        self._consecutive_failures += 1
        self._consecutive_successes = 0
        if self._consecutive_failures >= self.config.failure_threshold:
            self._open()

    def _open(self) -> None:
        self._state = CircuitState.OPEN
        self._opened_at = time.monotonic()
        self._consecutive_failures = 0
        self._consecutive_successes = 0
        logger.warning("provider=%s circuit OPEN (failures exceeded threshold)", self.provider_name)

    def _close(self) -> None:
        self._state = CircuitState.CLOSED
        self._opened_at = None
        self._consecutive_failures = 0
        self._consecutive_successes = 0
        logger.info("provider=%s circuit HALF_OPEN->CLOSED (recovered)", self.provider_name)

    def reset(self) -> None:
        """Manually force the breaker back to CLOSED (e.g. via admin/router endpoint)."""
        self._close()

    def status(self) -> CircuitBreakerStatus:
        return CircuitBreakerStatus(
            provider=self.provider_name,
            state=self.state,
            consecutive_failures=self._consecutive_failures,
            consecutive_successes=self._consecutive_successes,
            opened_at=self._opened_at,
            half_open_calls_in_flight=self._half_open_calls_in_flight,
        )

    async def call(self, func: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any) -> T:
        current_state = self.state

        if current_state == CircuitState.OPEN:
            raise CircuitBreakerOpenError(self.provider_name, self._retry_after())

        if current_state == CircuitState.HALF_OPEN:
            if self._half_open_calls_in_flight >= self.config.half_open_max_calls:
                raise CircuitBreakerOpenError(self.provider_name, self._retry_after())
            self._half_open_calls_in_flight += 1

        try:
            result = await func(*args, **kwargs)
        except Exception:
            self._on_failure()
            raise
        else:
            self._on_success()
            return result


class CircuitBreakerRegistry:
    """Holds one CircuitBreaker per provider so state persists across requests."""

    def __init__(self, default_config: CircuitBreakerConfig | None = None):
        self._default_config = default_config or CircuitBreakerConfig()
        self._breakers: dict[str, CircuitBreaker] = {}

    def get(self, provider_name: str) -> CircuitBreaker:
        if provider_name not in self._breakers:
            self._breakers[provider_name] = CircuitBreaker(provider_name, self._default_config)
        return self._breakers[provider_name]

    def all_status(self) -> list[CircuitBreakerStatus]:
        return [b.status() for b in self._breakers.values()]

    def reset(self, provider_name: str) -> None:
        self.get(provider_name).reset()

    def reset_all(self) -> None:
        for b in self._breakers.values():
            b.reset()


# Module-level singleton registry shared across the service/router.
circuit_breaker_registry = CircuitBreakerRegistry()
