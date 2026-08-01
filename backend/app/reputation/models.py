"""
models.py — ORM model for the `provider_reputation` table.

Each row tracks the rolling trust profile of a single AI provider
(e.g. "openai:gpt-4o", "groq:llama-3.1-70b", "ollama:mistral").
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    DateTime,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ProviderReputation(Base):
    """
    Rolling reputation record for an AI provider/agent.

    Trust Score formula (see scoring.py for implementation):
        trust_score = 0.40 * success_component
                     + 0.30 * rating_component
                     + 0.20 * speed_component
                     + 0.10 * reliability_component
    """

    __tablename__ = "provider_reputation"
    __table_args__ = (
        UniqueConstraint("provider", name="uq_provider_reputation_provider"),
        Index("ix_provider_reputation_trust_score", "trust_score"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Provider identifier, e.g. "openai:gpt-4o" or "groq:llama-3.1-70b"
    provider = Column(String(255), nullable=False)

    # Computed composite score (0-100)
    trust_score = Column(Float, nullable=False, default=0.0)

    # Raw rolling metrics used to compute trust_score
    avg_latency = Column(Float, nullable=False, default=0.0)      # milliseconds
    success_rate = Column(Float, nullable=False, default=0.0)     # 0-100 (%)
    failure_rate = Column(Float, nullable=False, default=0.0)     # 0-100 (%)
    rating = Column(Float, nullable=False, default=0.0)           # 0-5 stars

    # Bookkeeping counters
    total_requests = Column(Integer, nullable=False, default=0)
    total_successes = Column(Integer, nullable=False, default=0)
    total_failures = Column(Integer, nullable=False, default=0)
    total_ratings = Column(Integer, nullable=False, default=0)
    rating_sum = Column(Float, nullable=False, default=0.0)

    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<ProviderReputation provider={self.provider!r} "
            f"trust_score={self.trust_score:.2f} "
            f"success_rate={self.success_rate:.1f}% "
            f"rating={self.rating:.2f}>"
        )
