"""
integrations/huggingface.py

HuggingFace provider implementation via the HF Inference API
(router.huggingface.co / api-inference.huggingface.co style text-generation
endpoint).
"""

from __future__ import annotations

from typing import Any

import requests

from .base import AIProvider, AIProviderError, AIResponse, TokenUsage

DEFAULT_BASE_URL = "https://api-inference.huggingface.co/models"
DEFAULT_MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"


class HuggingFaceProvider(AIProvider):
    provider_name = "huggingface"

    def __init__(self, api_key: str | None = None, model: str | None = None, base_url: str = DEFAULT_BASE_URL, **kwargs: Any):
        super().__init__(api_key=api_key, model=model or DEFAULT_MODEL, **kwargs)
        self.base_url = base_url.rstrip("/")

    def _call(self, prompt: str, **kwargs: Any) -> AIResponse:
        api_key = self._require_api_key()
        model = kwargs.pop("model", self.model)

        payload = {
            "inputs": prompt,
            "parameters": {
                "temperature": kwargs.pop("temperature", 0.7),
                "max_new_tokens": kwargs.pop("max_tokens", 1024),
                "return_full_text": False,
            },
        }
        payload["parameters"].update(kwargs.pop("parameters", {}))

        try:
            resp = requests.post(
                f"{self.base_url}/{model}",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=kwargs.get("timeout", 60),
            )
        except requests.RequestException as exc:
            raise AIProviderError(f"network error: {exc}", provider=self.provider_name, retryable=True) from exc

        if resp.status_code == 503:
            # Model is loading on HF's side -- worth a retry.
            raise AIProviderError(
                "HuggingFace model is currently loading, retry shortly",
                provider=self.provider_name,
                retryable=True,
                status_code=503,
                raw=resp.text,
            )

        if resp.status_code != 200:
            retryable = resp.status_code >= 500 or resp.status_code == 429
            raise AIProviderError(
                f"HuggingFace API error ({resp.status_code}): {resp.text[:300]}",
                provider=self.provider_name,
                retryable=retryable,
                status_code=resp.status_code,
                raw=resp.text,
            )

        data = resp.json()
        # HF text-generation responses are typically a list of {"generated_text": ...}
        try:
            if isinstance(data, list):
                content = data[0]["generated_text"]
            elif isinstance(data, dict) and "generated_text" in data:
                content = data["generated_text"]
            else:
                raise KeyError("generated_text")
        except (KeyError, IndexError, TypeError) as exc:
            raise AIProviderError(
                f"unexpected HuggingFace response shape: {data}",
                provider=self.provider_name,
                retryable=False,
                raw=data,
            ) from exc

        return AIResponse(
            content=content,
            provider=self.provider_name,
            model=model,
            latency_ms=0,
            usage=TokenUsage(),  # HF inference API does not return token usage
            finish_reason=None,
            raw=data,
        )
