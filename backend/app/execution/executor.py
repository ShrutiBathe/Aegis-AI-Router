"""
executor.py — Module 2 (Execution Engine)

Owns exactly one job: "Call AI Integration" -> "Receive Response" from the
module's flow diagram. It knows nothing about HTTP or the database, and it
never raises past its own boundary — every outcome (success, timeout,
adapter error) comes back as an ExecutionResult so callers have one shape
to handle.
"""
from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any, Optional, Protocol

logger = logging.getLogger("execution_engine.executor")


class AgentNotSupportedError(Exception):
    """Raised when the requested agent has no registered AI Integration client."""


class AIIntegrationClient(Protocol):
    """
    Contract every AI Integration Layer adapter must implement.

    Concrete adapters (e.g. OpenAIIntegrationClient, AnthropicIntegrationClient)
    live outside this file — in the AI Integration Layer module — and get
    wired in via `Executor.register_client(...)` at app startup.
    """

    async def call(self, prompt: str, params: Optional[dict[str, Any]]) -> str:
        """Send prompt to the underlying AI service and return its text response."""
        ...


@dataclass
class ExecutionResult:
    success: bool
    response: Optional[str]
    error: Optional[str]
    latency_ms: float
    attempts: int


class Executor:
    """
    Executes a validated request against the AI Integration Layer, with a
    bounded retry-with-backoff policy and a hard timeout per attempt.
    """

    def __init__(
        self,
        timeout_seconds: float = 15.0,
        max_retries: int = 2,
        backoff_base_seconds: float = 0.5,
    ) -> None:
        self._clients: dict[str, AIIntegrationClient] = {}
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.backoff_base_seconds = backoff_base_seconds

    def register_client(self, agent_name: str, client: AIIntegrationClient) -> None:
        """Wire an AI Integration Layer adapter to an agent name (case-insensitive)."""
        self._clients[agent_name.lower()] = client

    def supports(self, agent_name: str) -> bool:
        return agent_name.lower() in self._clients

    async def execute(
        self, agent: str, prompt: str, params: Optional[dict[str, Any]] = None
    ) -> ExecutionResult:
        client = self._clients.get(agent.lower())
        if client is None:
            raise AgentNotSupportedError(f"No AI Integration client registered for agent '{agent}'")

        start = time.perf_counter()
        attempts = 0
        last_error: Optional[str] = None

        while attempts <= self.max_retries:
            attempts += 1
            try:
                response = await asyncio.wait_for(
                    client.call(prompt, params), timeout=self.timeout_seconds
                )
                return ExecutionResult(
                    success=True,
                    response=response,
                    error=None,
                    latency_ms=(time.perf_counter() - start) * 1000,
                    attempts=attempts,
                )
            except asyncio.TimeoutError:
                last_error = f"AI Integration Layer timed out after {self.timeout_seconds}s"
                logger.warning(
                    "attempt %s/%s for agent=%s timed out", attempts, self.max_retries + 1, agent
                )
            except Exception as exc:  # noqa: BLE001 — normalize any adapter-side failure
                last_error = str(exc)
                logger.warning(
                    "attempt %s/%s for agent=%s failed: %s", attempts, self.max_retries + 1, agent, exc
                )

            if attempts <= self.max_retries:
                await asyncio.sleep(self.backoff_base_seconds * attempts)

        return ExecutionResult(
            success=False,
            response=None,
            error=last_error or "Unknown execution failure",
            latency_ms=(time.perf_counter() - start) * 1000,
            attempts=attempts,
        )
