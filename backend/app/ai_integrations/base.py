"""
integrations/base.py

Common interface that every AI provider integration in Aegis AI Router
must implement. This is Module 3 of Team B2 (Service Execution &
Marketplace Operations).

Design goals:
- Every provider returns the SAME response shape (AIResponse), regardless
  of how different the underlying vendor API looks. This is what lets the
  Execution Engine and Self-Healing layer treat all providers uniformly.
- Errors never raise raw vendor exceptions up to the Execution Engine.
  They are normalized into AIProviderError so Self-Healing can catch a
  single exception type and decide whether to retry / fail over.
- Timing + token usage are captured here so History/Analytics/Reputation
  don't need to know provider-specific response formats.
"""

from __future__ import annotations

import time
import abc
from dataclasses import dataclass, field
from typing import Any, Optional


class AIProviderError(Exception):
    """
    Normalized error raised by any provider integration.

    The Self-Healing module should catch this (not provider-specific
    exceptions) and use `retryable` to decide whether to retry the same
    provider, fail over to a backup agent, or surface the error.
    """

    def __init__(
        self,
        message: str,
        provider: str,
        *,
        retryable: bool = True,
        status_code: Optional[int] = None,
        raw: Any = None,
    ):
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.retryable = retryable
        self.status_code = status_code
        self.raw = raw

    def __repr__(self) -> str:
        return (
            f"AIProviderError(provider={self.provider!r}, "
            f"status_code={self.status_code!r}, retryable={self.retryable!r}, "
            f"message={self.message!r})"
        )


@dataclass
class TokenUsage:
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


@dataclass
class AIResponse:
    """Normalized response returned by every provider's generate()."""

    content: str
    provider: str
    model: str
    latency_ms: float
    usage: TokenUsage = field(default_factory=TokenUsage)
    finish_reason: Optional[str] = None
    raw: Any = None  # original vendor payload, kept for debugging/analytics

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "provider": self.provider,
            "model": self.model,
            "latency_ms": self.latency_ms,
            "usage": {
                "prompt_tokens": self.usage.prompt_tokens,
                "completion_tokens": self.usage.completion_tokens,
                "total_tokens": self.usage.total_tokens,
            },
            "finish_reason": self.finish_reason,
        }


class AIProvider(abc.ABC):
    """
    Abstract base class every provider integration must implement.

    Subclasses must set `provider_name` and implement `_call(prompt, **kwargs)`
    which performs the actual vendor request and returns an AIResponse.
    `generate()` wraps `_call` with timing + uniform error handling so
    subclasses stay focused on the vendor-specific request/response mapping.
    """

    provider_name: str = "base"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, **kwargs: Any):
        self.api_key = api_key
        self.model = model
        self.extra_config = kwargs

    # ---- public interface -------------------------------------------------

    def generate(self, prompt: str, **kwargs: Any) -> AIResponse:
        """
        Generate a completion for `prompt`. This is the method the
        Execution Engine calls. It should never raise a vendor-specific
        exception -- only AIProviderError.
        """
        if not prompt or not isinstance(prompt, str):
            raise AIProviderError(
                "prompt must be a non-empty string",
                provider=self.provider_name,
                retryable=False,
            )

        start = time.monotonic()
        try:
            response = self._call(prompt, **kwargs)
        except AIProviderError:
            raise
        except Exception as exc:  # noqa: BLE001 - intentionally broad; normalize everything
            raise AIProviderError(
                f"{self.provider_name} request failed: {exc}",
                provider=self.provider_name,
                retryable=True,
                raw=exc,
            ) from exc

        response.latency_ms = round((time.monotonic() - start) * 1000, 2)
        return response

    async def agenerate(self, prompt: str, **kwargs: Any) -> AIResponse:
        """
        Optional async entrypoint. Default implementation just runs the
        sync path in a thread so providers aren't forced to implement
        async transport unless they want to (e.g. for streaming later).
        """
        import asyncio

        return await asyncio.to_thread(self.generate, prompt, **kwargs)

    def health_check(self) -> bool:
        """
        Lightweight check used by Self-Healing / routing to decide if a
        provider is worth trying at all before spending a real request on
        it. Providers can override with a cheaper vendor-specific check.
        """
        try:
            self.generate("ping", max_tokens=1)
            return True
        except AIProviderError:
            return False

    # ---- subclass responsibility -------------------------------------------

    @abc.abstractmethod
    def _call(self, prompt: str, **kwargs: Any) -> AIResponse:
        """Perform the actual vendor call and return an AIResponse (latency_ms can be left as 0, it's overwritten)."""
        raise NotImplementedError

    def _require_api_key(self) -> str:
        if not self.api_key:
            raise AIProviderError(
                f"Missing API key for provider '{self.provider_name}'",
                provider=self.provider_name,
                retryable=False,
            )
        return self.api_key
