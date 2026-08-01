"""
provider_interface.py
----------------------
Thin adapter over the existing "AI Integrations" module (OpenAI, Gemini,
Claude, Groq, Ollama, etc.).

This module intentionally does NOT reimplement provider clients. It defines
the contract the Self-Healing module expects, and imports the real registry
from the AI Integrations module. If that module hasn't been wired into this
package path yet, a lightweight in-memory stub is used instead so the
Self-Healing module remains importable and testable on its own.

Adjust `AI_INTEGRATIONS_IMPORT_PATH` below to match your actual package
layout once this module is merged next to the AI Integrations module.
"""

from __future__ import annotations

import time
import random
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass
class AIProviderResponse:
    provider: str
    content: str
    latency_ms: float
    metadata: dict[str, Any] = field(default_factory=dict)


class AIProviderError(Exception):
    """Raised by a provider client when a call fails (timeout, 5xx, rate limit, etc.)."""

    def __init__(self, provider: str, message: str, retryable: bool = True):
        self.provider = provider
        self.retryable = retryable
        super().__init__(f"[{provider}] {message}")


@runtime_checkable
class AIProviderClient(Protocol):
    """Contract every provider client in the AI Integrations module must satisfy."""

    provider_name: str

    async def execute(self, prompt: str, **kwargs: Any) -> AIProviderResponse:
        ...


@runtime_checkable
class AIProviderRegistry(Protocol):
    """Contract for the registry that looks up/ranks provider clients."""

    def get_client(self, provider_name: str) -> AIProviderClient:
        ...

    def list_providers(self) -> list[str]:
        ...


# ---------------------------------------------------------------------------
# Real integration point
# ---------------------------------------------------------------------------
# INTEGRATION UPDATE: this now imports the real adapter at
# app/ai_integrations/registry.py (see that file for what it wraps).
# The import previously had no `app.` prefix, which doesn't resolve
# under this project's package layout (see app/main.py) — it silently
# fell through to the stub below on every request instead of raising,
# so Self-Healing was always talking to fake in-memory responses.

AI_INTEGRATIONS_IMPORT_PATH = "app.ai_integrations.registry"

try:
    from app.ai_integrations.registry import provider_registry  # type: ignore

except ImportError:

    class _StubProviderClient:
        """Fallback stub used only when the real AI Integrations module isn't
        available on the import path yet. Simulates latency and occasional
        failure so retry/circuit-breaker/failover logic can be exercised
        end-to-end without the real providers wired in."""

        def __init__(self, provider_name: str, failure_rate: float = 0.0):
            self.provider_name = provider_name
            self.failure_rate = failure_rate

        async def execute(self, prompt: str, **kwargs: Any) -> AIProviderResponse:
            start = time.perf_counter()
            if random.random() < self.failure_rate:
                raise AIProviderError(self.provider_name, "simulated failure", retryable=True)
            latency_ms = (time.perf_counter() - start) * 1000
            return AIProviderResponse(
                provider=self.provider_name,
                content=f"[stub:{self.provider_name}] response to: {prompt[:60]}",
                latency_ms=latency_ms,
                metadata={"stub": True},
            )

    class _StubProviderRegistry:
        def __init__(self) -> None:
            self._clients = {
                "openai": _StubProviderClient("openai", failure_rate=0.0),
                "gemini": _StubProviderClient("gemini", failure_rate=0.0),
                "claude": _StubProviderClient("claude", failure_rate=0.0),
                "groq": _StubProviderClient("groq", failure_rate=0.0),
                "ollama": _StubProviderClient("ollama", failure_rate=0.0),
            }

        def get_client(self, provider_name: str) -> AIProviderClient:
            try:
                return self._clients[provider_name]
            except KeyError:
                raise AIProviderError(provider_name, "unknown provider", retryable=False)

        def list_providers(self) -> list[str]:
            return list(self._clients.keys())

    provider_registry: AIProviderRegistry = _StubProviderRegistry()  # type: ignore
