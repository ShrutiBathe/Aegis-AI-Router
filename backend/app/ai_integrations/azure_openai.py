"""
integrations/azure_openai.py

Azure OpenAI provider implementation. Unlike vanilla OpenAI, Azure requires
a per-resource endpoint and a deployment name (rather than a model name),
plus an api-version query parameter.
"""

from __future__ import annotations

from typing import Any

import requests

from .base import AIProvider, AIProviderError, AIResponse, TokenUsage

DEFAULT_API_VERSION = "2024-06-01"


class AzureOpenAIProvider(AIProvider):
    provider_name = "azure_openai"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        *,
        endpoint: str | None = None,
        deployment: str | None = None,
        api_version: str = DEFAULT_API_VERSION,
        **kwargs: Any,
    ):
        """
        `endpoint`   e.g. "https://my-resource.openai.azure.com"
        `deployment` the Azure deployment name (this is what Azure routes on,
                     NOT the underlying model name -- but we accept `model`
                     as an alias for convenience since callers coming from
                     other providers will pass `model`).
        """
        super().__init__(api_key=api_key, model=model, **kwargs)
        if not endpoint:
            raise AIProviderError(
                "Azure OpenAI requires an `endpoint` (e.g. https://<resource>.openai.azure.com)",
                provider=self.provider_name,
                retryable=False,
            )
        self.endpoint = endpoint.rstrip("/")
        self.deployment = deployment or model
        self.api_version = api_version

    def _call(self, prompt: str, **kwargs: Any) -> AIResponse:
        api_key = self._require_api_key()
        deployment = kwargs.pop("deployment", None) or self.deployment
        if not deployment:
            raise AIProviderError(
                "Azure OpenAI requires a `deployment` name",
                provider=self.provider_name,
                retryable=False,
            )

        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.pop("temperature", 0.7),
            "max_tokens": kwargs.pop("max_tokens", 1024),
        }
        payload.update(kwargs)

        url = (
            f"{self.endpoint}/openai/deployments/{deployment}/chat/completions"
            f"?api-version={self.api_version}"
        )

        try:
            resp = requests.post(
                url,
                headers={
                    "api-key": api_key,
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
                f"Azure OpenAI API error ({resp.status_code}): {resp.text[:300]}",
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
                f"unexpected Azure OpenAI response shape: {data}",
                provider=self.provider_name,
                retryable=False,
                raw=data,
            ) from exc

        usage = data.get("usage", {})
        return AIResponse(
            content=content,
            provider=self.provider_name,
            model=deployment,
            latency_ms=0,
            usage=TokenUsage(
                prompt_tokens=usage.get("prompt_tokens"),
                completion_tokens=usage.get("completion_tokens"),
                total_tokens=usage.get("total_tokens"),
            ),
            finish_reason=choice.get("finish_reason"),
            raw=data,
        )
