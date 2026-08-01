"""
integrations/factory.py

Registry + factory for AI providers. This is the entry point the
Execution Engine / AI Integration Layer uses: it doesn't need to know
about individual provider classes, just a provider name string (which
presumably comes from the ranked agent selection upstream).

    from integrations.factory import get_provider

    provider = get_provider("claude", api_key=os.environ["ANTHROPIC_API_KEY"])
    response = provider.generate("Summarize x402 in one sentence.")
"""

from __future__ import annotations

from typing import Any, Type

from .base import AIProvider, AIProviderError
from .openai import OpenAIProvider
from .gemini import GeminiProvider
from .claude import ClaudeProvider
from .groq import GroqProvider
from .ollama import OllamaProvider
from .huggingface import HuggingFaceProvider
from .azure_openai import AzureOpenAIProvider

_REGISTRY: dict[str, Type[AIProvider]] = {
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "claude": ClaudeProvider,
    "groq": GroqProvider,
    "ollama": OllamaProvider,
    "huggingface": HuggingFaceProvider,
    "hf": HuggingFaceProvider,  # alias
    "azure_openai": AzureOpenAIProvider,
    "azure": AzureOpenAIProvider,  # alias
}


def register_provider(name: str, cls: Type[AIProvider]) -> None:
    """Allow new providers to be plugged in without editing this file."""
    _REGISTRY[name.lower()] = cls


def available_providers() -> list[str]:
    return sorted(_REGISTRY.keys())


def get_provider(name: str, **kwargs: Any) -> AIProvider:
    """
    Instantiate a provider by name. Raises AIProviderError (not KeyError)
    if the name is unknown, so callers in the Execution Engine can handle
    it the same way as any other provider failure.
    """
    key = name.lower().strip()
    cls = _REGISTRY.get(key)
    if cls is None:
        raise AIProviderError(
            f"Unknown AI provider '{name}'. Available: {', '.join(available_providers())}",
            provider=name,
            retryable=False,
        )
    return cls(**kwargs)
