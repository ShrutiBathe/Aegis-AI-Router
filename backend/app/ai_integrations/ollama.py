"""
integrations/ollama.py

Ollama provider implementation. Talks to a local (or self-hosted) Ollama
server. No API key required by default since Ollama typically runs
unauthenticated on localhost, but `api_key`/extra headers are supported
for proxied/secured deployments.
"""

from __future__ import annotations

from typing import Any

import requests

from .base import AIProvider, AIProviderError, AIResponse, TokenUsage

DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3"


class OllamaProvider(AIProvider):
    provider_name = "ollama"

    def __init__(self, api_key: str | None = None, model: str | None = None, base_url: str = DEFAULT_BASE_URL, **kwargs: Any):
        # api_key is optional for Ollama; base class only requires it if used.
        super().__init__(api_key=api_key, model=model or DEFAULT_MODEL, **kwargs)
        self.base_url = base_url.rstrip("/")

    def _call(self, prompt: str, **kwargs: Any) -> AIResponse:
        payload = {
            "model": kwargs.pop("model", self.model),
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.pop("temperature", 0.7),
            },
        }
        if "max_tokens" in kwargs:
            payload["options"]["num_predict"] = kwargs.pop("max_tokens")
        payload["options"].update(kwargs.pop("options", {}))

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                headers=headers,
                json=payload,
                timeout=kwargs.get("timeout", 120),
            )
        except requests.RequestException as exc:
            raise AIProviderError(
                f"could not reach Ollama at {self.base_url}: {exc}",
                provider=self.provider_name,
                retryable=True,
            ) from exc

        if resp.status_code != 200:
            retryable = resp.status_code >= 500
            raise AIProviderError(
                f"Ollama error ({resp.status_code}): {resp.text[:300]}",
                provider=self.provider_name,
                retryable=retryable,
                status_code=resp.status_code,
                raw=resp.text,
            )

        data = resp.json()
        if "response" not in data:
            raise AIProviderError(
                f"unexpected Ollama response shape: {data}",
                provider=self.provider_name,
                retryable=False,
                raw=data,
            )

        return AIResponse(
            content=data["response"],
            provider=self.provider_name,
            model=data.get("model", self.model),
            latency_ms=0,
            usage=TokenUsage(
                prompt_tokens=data.get("prompt_eval_count"),
                completion_tokens=data.get("eval_count"),
                total_tokens=(
                    (data.get("prompt_eval_count") or 0) + (data.get("eval_count") or 0)
                    if data.get("prompt_eval_count") is not None or data.get("eval_count") is not None
                    else None
                ),
            ),
            finish_reason="stop" if data.get("done") else None,
            raw=data,
        )
