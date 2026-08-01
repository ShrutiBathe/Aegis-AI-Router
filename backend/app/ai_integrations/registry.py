"""
app/ai_integrations/registry.py

`self_healing/provider_interface.py` already tries to import this exact
module (`ai_integrations.registry.provider_registry`) and only falls
back to an in-memory fake provider when the import fails — which it
always did, since this file didn't exist and the import had no `app.`
prefix. That silent fallback is fixed on the self_healing side (see the
diff to provider_interface.py); this file is the other half: the real
registry it's now able to find.

This is a pure adapter — it does not reimplement any provider logic.
It wraps `ai_integrations.factory.get_provider(name)` (which returns an
`AIProvider` with `.agenerate() -> AIResponse`) behind the
`AIProviderClient` protocol self_healing's retry/circuit-breaker/
failover code already operates on (`.execute() -> AIProviderResponse`).

API keys are read from environment variables per provider. Ollama needs
no key (local). Anything not configured raises AIProviderError with
retryable=False so failover moves on to the next candidate immediately
instead of burning retry attempts on a guaranteed-to-fail provider.
"""
from __future__ import annotations

import os
from typing import Any

from .base import AIProvider, AIProviderError as IntegrationsAIProviderError
from .factory import get_provider

# provider name -> env var holding its API key. Providers not listed here
# (e.g. "ollama") are assumed to need no key.
_API_KEY_ENV = {
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "claude": "ANTHROPIC_API_KEY",
    "groq": "GROQ_API_KEY",
    "huggingface": "HUGGINGFACE_API_KEY",
    "hf": "HUGGINGFACE_API_KEY",
    "azure_openai": "AZURE_OPENAI_API_KEY",
    "azure": "AZURE_OPENAI_API_KEY",
}


def _build_provider(name: str) -> AIProvider:
    key = name.lower().strip()
    kwargs: dict[str, Any] = {}
    env_var = _API_KEY_ENV.get(key)
    if env_var:
        kwargs["api_key"] = os.environ.get(env_var)
    return get_provider(key, **kwargs)


class _AIIntegrationsClient:
    """Adapts one AIProvider instance to self_healing's AIProviderClient protocol."""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    async def execute(self, prompt: str, **kwargs: Any):
        # Imported lazily to avoid a hard import-time dependency from
        # ai_integrations -> self_healing (keeps both modules independently
        # importable/testable, matching the rest of this codebase's style).
        from app.self_healing.provider_interface import AIProviderError, AIProviderResponse

        provider = _build_provider(self.provider_name)
        try:
            response = await provider.agenerate(prompt, **kwargs)
        except IntegrationsAIProviderError as exc:
            # Normalize ai_integrations' error type into self_healing's,
            # preserving the retryable flag so circuit-breaker/retry
            # behavior is unaffected by which module raised it.
            raise AIProviderError(exc.provider, exc.message, retryable=exc.retryable) from exc

        return AIProviderResponse(
            provider=response.provider,
            content=response.content,
            latency_ms=response.latency_ms,
            metadata={
                "model": response.model,
                "finish_reason": response.finish_reason,
                "usage": response.usage.__dict__ if response.usage else None,
            },
        )


class _AIIntegrationsRegistry:
    def get_client(self, provider_name: str) -> _AIIntegrationsClient:
        return _AIIntegrationsClient(provider_name.lower().strip())

    def list_providers(self) -> list[str]:
        from .factory import available_providers

        return available_providers()


provider_registry = _AIIntegrationsRegistry()
