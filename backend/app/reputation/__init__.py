"""
Reputation Module — Aegis AI Router
Team B2: Service Execution & Marketplace Operations

Maintains trust scores and provider ratings for every AI provider
registered in the marketplace (OpenAI, Gemini, Claude, Groq, Ollama, etc.)
"""

from .models import ProviderReputation
from .schemas import (
    ProviderReputationCreate,
    ProviderReputationUpdate,
    ProviderReputationRead,
    ReputationEventIn,
)
from .scoring import TrustScoreCalculator, TrustScoreBreakdown
from .service import ReputationService
from .router import router as reputation_router

__all__ = [
    "ProviderReputation",
    "ProviderReputationCreate",
    "ProviderReputationUpdate",
    "ProviderReputationRead",
    "ReputationEventIn",
    "TrustScoreCalculator",
    "TrustScoreBreakdown",
    "ReputationService",
    "reputation_router",
]
