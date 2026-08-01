"""
Aegis AI Router - Module 3: AI Integrations

Connects multiple external AI providers behind one common interface
(AIProvider.generate) so the Execution Engine can call any ranked/selected
agent the same way, and Self-Healing can fail over between providers
without provider-specific branching.
"""

from .base import AIProvider, AIProviderError, AIResponse, TokenUsage
from .factory import get_provider, register_provider, available_providers

from .openai import OpenAIProvider
from .gemini import GeminiProvider
from .claude import ClaudeProvider
from .groq import GroqProvider
from .ollama import OllamaProvider
from .huggingface import HuggingFaceProvider
from .azure_openai import AzureOpenAIProvider

__all__ = [
    "AIProvider",
    "AIProviderError",
    "AIResponse",
    "TokenUsage",
    "get_provider",
    "register_provider",
    "available_providers",
    "OpenAIProvider",
    "GeminiProvider",
    "ClaudeProvider",
    "GroqProvider",
    "OllamaProvider",
    "HuggingFaceProvider",
    "AzureOpenAIProvider",
]
