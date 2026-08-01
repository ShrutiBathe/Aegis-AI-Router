"""
integrations/gemini.py

Google Gemini provider implementation via the Generative Language REST API.
"""

from __future__ import annotations

from typing import Any

import requests

from .base import AIProvider, AIProviderError, AIResponse, TokenUsage

DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = "gemini-1.5-flash"


class GeminiProvider(AIProvider):
    provider_name = "gemini"

    def __init__(self, api_key: str | None = None, model: str | None = None, base_url: str = DEFAULT_BASE_URL, **kwargs: Any):
        super().__init__(api_key=api_key, model=model or DEFAULT_MODEL, **kwargs)
        self.base_url = base_url.rstrip("/")

    def _call(self, prompt: str, **kwargs: Any) -> AIResponse:
        api_key = self._require_api_key()
        model = kwargs.pop("model", self.model)

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": kwargs.pop("temperature", 0.7),
                "maxOutputTokens": kwargs.pop("max_tokens", 1024),
            },
        }
        payload["generationConfig"].update(kwargs.pop("generation_config", {}))

        url = f"{self.base_url}/models/{model}:generateContent?key={api_key}"

        try:
            resp = requests.post(url, json=payload, timeout=kwargs.get("timeout", 60))
        except requests.RequestException as exc:
            raise AIProviderError(f"network error: {exc}", provider=self.provider_name, retryable=True) from exc

        if resp.status_code != 200:
            retryable = resp.status_code >= 500 or resp.status_code == 429
            raise AIProviderError(
                f"Gemini API error ({resp.status_code}): {resp.text[:300]}",
                provider=self.provider_name,
                retryable=retryable,
                status_code=resp.status_code,
                raw=resp.text,
            )

        data = resp.json()
        try:
            candidate = data["candidates"][0]
            content = "".join(p.get("text", "") for p in candidate["content"]["parts"])
        except (KeyError, IndexError) as exc:
            raise AIProviderError(
                f"unexpected Gemini response shape: {data}",
                provider=self.provider_name,
                retryable=False,
                raw=data,
            ) from exc

        usage_meta = data.get("usageMetadata", {})
        return AIResponse(
            content=content,
            provider=self.provider_name,
            model=model,
            latency_ms=0,
            usage=TokenUsage(
                prompt_tokens=usage_meta.get("promptTokenCount"),
                completion_tokens=usage_meta.get("candidatesTokenCount"),
                total_tokens=usage_meta.get("totalTokenCount"),
            ),
            finish_reason=candidate.get("finishReason"),
            raw=data,
        )
