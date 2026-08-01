"""
schemas.py — Pydantic (v2) request/response models for the Reputation API.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class ReputationEventIn(BaseModel):
    """
    Payload emitted by the Execution / Self-Healing modules after every
    task completion. This is the raw event the reputation system consumes
    to update a provider's rolling metrics.
    """

    provider: str = Field(..., description="Provider identifier, e.g. 'openai:gpt-4o'")
    success: bool = Field(..., description="Whether the execution succeeded")
    latency_ms: float = Field(..., ge=0, description="Response time in milliseconds")
    rating: Optional[float] = Field(
        None, ge=0, le=5, description="Optional user rating (0-5) for this execution"
    )


class ProviderReputationCreate(BaseModel):
    provider: str
    avg_latency: float = 0.0
    success_rate: float = 0.0
    failure_rate: float = 0.0
    rating: float = 0.0


class ProviderReputationUpdate(BaseModel):
    avg_latency: Optional[float] = None
    success_rate: Optional[float] = None
    failure_rate: Optional[float] = None
    rating: Optional[float] = None


class ProviderReputationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    provider: str
    trust_score: float
    avg_latency: float
    success_rate: float
    failure_rate: float
    rating: float
    total_requests: int
    total_successes: int
    total_failures: int
    total_ratings: int
    created_at: datetime
    updated_at: datetime


class TrustScoreBreakdownOut(BaseModel):
    """Transparent breakdown of how a trust score was derived."""

    provider: str
    trust_score: float
    success_component: float
    rating_component: float
    speed_component: float
    reliability_component: float
    weights: dict = Field(
        default_factory=lambda: {
            "success": 0.40,
            "rating": 0.30,
            "speed": 0.20,
            "reliability": 0.10,
        }
    )


class LeaderboardEntry(BaseModel):
    rank: int
    provider: str
    trust_score: float
    success_rate: float
    rating: float
    avg_latency: float
    total_requests: int
