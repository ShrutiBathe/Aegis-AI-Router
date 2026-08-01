"""
retry.py
--------
Retry strategy: exponential backoff with jitter, configurable per-call.

    Retry(config).run(func, *args, **kwargs)

Only exceptions marked `retryable=True` (see provider_interface.AIProviderError)
are retried; anything else is raised immediately.
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, TypeVar

from .provider_interface import AIProviderError

logger = logging.getLogger("self_healing.retry")

T = TypeVar("T")


class RetryExhaustedError(Exception):
    """Raised when all retry attempts for a single provider have been used up."""

    def __init__(self, provider: str, attempts: int, last_error: Exception):
        self.provider = provider
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(
            f"[{provider}] retry exhausted after {attempts} attempt(s): {last_error}"
        )


@dataclass
class RetryConfig:
    max_attempts: int = 3
    base_delay_seconds: float = 0.5
    max_delay_seconds: float = 8.0
    backoff_multiplier: float = 2.0
    jitter_ratio: float = 0.2  # +/- 20% randomization on each delay
    timeout_seconds: float | None = 10.0  # per-attempt timeout


@dataclass
class RetryAttemptLog:
    attempt: int
    delay_before_seconds: float
    error: str | None
    duration_ms: float


class Retry:
    """Executes a coroutine with exponential backoff retry."""

    def __init__(self, config: RetryConfig | None = None):
        self.config = config or RetryConfig()

    def _compute_delay(self, attempt: int) -> float:
        raw = self.config.base_delay_seconds * (self.config.backoff_multiplier ** (attempt - 1))
        raw = min(raw, self.config.max_delay_seconds)
        jitter = raw * self.config.jitter_ratio
        return max(0.0, raw + random.uniform(-jitter, jitter))

    async def run(
        self,
        func: Callable[..., Awaitable[T]],
        *args: Any,
        provider_name: str = "unknown",
        **kwargs: Any,
    ) -> tuple[T, list[RetryAttemptLog]]:
        """
        Runs `func` up to `max_attempts` times. Returns (result, attempt_log).
        Raises RetryExhaustedError if every attempt fails.
        Non-retryable errors (AIProviderError(retryable=False) or any other
        exception type not explicitly marked retryable) are raised immediately.
        """
        attempt_log: list[RetryAttemptLog] = []
        last_error: Exception | None = None

        for attempt in range(1, self.config.max_attempts + 1):
            delay = self._compute_delay(attempt) if attempt > 1 else 0.0
            if delay > 0:
                logger.info(
                    "provider=%s attempt=%d backing off %.2fs before retry",
                    provider_name, attempt, delay,
                )
                await asyncio.sleep(delay)

            start = time.perf_counter()
            try:
                coro = func(*args, **kwargs)
                if self.config.timeout_seconds:
                    result = await asyncio.wait_for(coro, timeout=self.config.timeout_seconds)
                else:
                    result = await coro

                duration_ms = (time.perf_counter() - start) * 1000
                attempt_log.append(
                    RetryAttemptLog(attempt=attempt, delay_before_seconds=delay,
                                    error=None, duration_ms=duration_ms)
                )
                logger.info("provider=%s attempt=%d succeeded in %.1fms",
                            provider_name, attempt, duration_ms)
                return result, attempt_log

            except asyncio.TimeoutError as exc:
                duration_ms = (time.perf_counter() - start) * 1000
                last_error = exc
                attempt_log.append(
                    RetryAttemptLog(attempt=attempt, delay_before_seconds=delay,
                                    error="timeout", duration_ms=duration_ms)
                )
                logger.warning("provider=%s attempt=%d timed out after %.1fms",
                               provider_name, attempt, duration_ms)
                continue  # timeouts are always retryable up to max_attempts

            except AIProviderError as exc:
                duration_ms = (time.perf_counter() - start) * 1000
                last_error = exc
                attempt_log.append(
                    RetryAttemptLog(attempt=attempt, delay_before_seconds=delay,
                                    error=str(exc), duration_ms=duration_ms)
                )
                if not exc.retryable:
                    logger.warning("provider=%s attempt=%d non-retryable error: %s",
                                   provider_name, attempt, exc)
                    raise
                logger.warning("provider=%s attempt=%d failed: %s", provider_name, attempt, exc)
                continue

            except Exception as exc:  # unexpected error type -> don't silently retry forever
                duration_ms = (time.perf_counter() - start) * 1000
                attempt_log.append(
                    RetryAttemptLog(attempt=attempt, delay_before_seconds=delay,
                                    error=str(exc), duration_ms=duration_ms)
                )
                logger.error("provider=%s attempt=%d unexpected error: %s",
                             provider_name, attempt, exc)
                raise

        raise RetryExhaustedError(provider_name, self.config.max_attempts, last_error or Exception("unknown"))
