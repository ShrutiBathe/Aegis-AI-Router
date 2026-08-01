"""
integrations/claude.py

Anthropic Claude provider implementation via the Messages REST API.
"""

from __future__ import annotations

from typing import Any

import requests

from .base import AIProvider, AIProviderError, AIResponse, TokenUsage

DEFAULT_BASE_URL = "https://api.anthropic.com/v1"
DEFAULT_MODEL = "claude-sonnet-4-6"
ANTHROPIC_VERSION = "2023-06-01"


class ClaudeProvider(AIProvider):
    provider_name = "claude"

    def __init__(self, api_key: str | None = None, model: str | None = None, base_url: str = DEFAULT_BASE_URL, **kwargs: Any):
        super().__init__(api_key=api_key, model=model or DEFAULT_MODEL, **kwargs)
        self.base_url = base_url.rstrip("/")

    def _call(self, prompt: str, **kwargs: Any) -> AIResponse:
        api_key = self._require_api_key()

        payload = {
            "model": kwargs.pop("model", self.model),
            "max_tokens": kwargs.pop("max_tokens", 1024),
            "messages": [{"role": "user", "content": prompt}],
        }
        if "temperature" in kwargs:
            payload["temperature"] = kwargs.pop("temperature")
        if "system" in kwargs:
            payload["system"] = kwargs.pop("system")
        payload.update(kwargs)

        try:
            resp = requests.post(
                f"{self.base_url}/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": ANTHROPIC_VERSION,
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=kwargs.get("timeout", 60),
            )
        except requests.RequestException as exc:
            raise AIProviderError(f"network error: {exc}", provider=self.provider_name, retryable=True) from exc

        if resp.status_code != 200:
            retryable = resp.status_code >= 500 or resp.status_code == 429
            raise AIProviderError(
                f"Claude API error ({resp.status_code}): {resp.text[:300]}",
                provider=self.provider_name,
                retryable=retryable,
                status_code=resp.status_code,
                raw=resp.text,
            )

        data = resp.json()
        try:
            content = "".join(block.get("text", "") for block in data["content"] if block.get("type") == "text")
        except KeyError as exc:
            raise AIProviderError(
                f"unexpected Claude response shape: {data}",
                provider=self.provider_name,
                retryable=False,
                raw=data,
            ) from exc

        usage = data.get("usage", {})
        prompt_tokens = usage.get("input_tokens")
        completion_tokens = usage.get("output_tokens")
        total_tokens = (
            prompt_tokens + completion_tokens
            if prompt_tokens is not None and completion_tokens is not None
            else None
        )

        return AIResponse(
            content=content,
            provider=self.provider_name,
            model=data.get("model", self.model),
            latency_ms=0,
            usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            ),
            finish_reason=data.get("stop_reason"),
            raw=data,
        )
