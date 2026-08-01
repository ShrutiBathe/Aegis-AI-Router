"""
integrations/groq.py

Groq provider implementation. Groq exposes an OpenAI-compatible Chat
Completions API, so this mirrors integrations/openai.py against Groq's
base URL and default model.
"""

from __future__ import annotations

from typing import Any

import requests

from .base import AIProvider, AIProviderError, AIResponse, TokenUsage

DEFAULT_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_MODEL = "llama-3.3-70b-versatile"


class GroqProvider(AIProvider):
    provider_name = "groq"

    def __init__(self, api_key: str | None = None, model: str | None = None, base_url: str = DEFAULT_BASE_URL, **kwargs: Any):
        super().__init__(api_key=api_key, model=model or DEFAULT_MODEL, **kwargs)
        self.base_url = base_url.rstrip("/")

    def _call(self, prompt: str, **kwargs: Any) -> AIResponse:
        api_key = self._require_api_key()

        payload = {
            "model": kwargs.pop("model", self.model),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.pop("temperature", 0.7),
            "max_tokens": kwargs.pop("max_tokens", 1024),
        }
        payload.update(kwargs)

        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
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
                f"Groq API error ({resp.status_code}): {resp.text[:300]}",
                provider=self.provider_name,
                retryable=retryable,
                status_code=resp.status_code,
                raw=resp.text,
            )

        data = resp.json()
        try:
            choice = data["choices"][0]
            content = choice["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise AIProviderError(
                f"unexpected Groq response shape: {data}",
                provider=self.provider_name,
                retryable=False,
                raw=data,
            ) from exc

        usage = data.get("usage", {})
        return AIResponse(
            content=content,
            provider=self.provider_name,
            model=data.get("model", self.model),
            latency_ms=0,
            usage=TokenUsage(
                prompt_tokens=usage.get("prompt_tokens"),
                completion_tokens=usage.get("completion_tokens"),
                total_tokens=usage.get("total_tokens"),
            ),
            finish_reason=choice.get("finish_reason"),
            raw=data,
        )
