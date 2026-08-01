"""
service.py — Business logic for the Reputation module.

Consumes execution events from the Execution / Self-Healing modules,
maintains rolling metrics per provider, and recomputes trust scores.
"""

from typing import List, Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from .models import ProviderReputation
from .scoring import TrustScoreCalculator, TrustScoreBreakdown
from .schemas import ReputationEventIn, LeaderboardEntry


class ReputationService:
    """
    Encapsulates all reputation reads/writes. Instantiate with an
    AsyncSession per-request (standard FastAPI dependency pattern).
    """

    def __init__(self, session: AsyncSession, calculator: Optional[TrustScoreCalculator] = None):
        self.session = session
        self.calculator = calculator or TrustScoreCalculator()

    # ------------------------------------------------------------------ #
    # Reads
    # ------------------------------------------------------------------ #

    async def get_by_provider(self, provider: str) -> Optional[ProviderReputation]:
        result = await self.session.execute(
            select(ProviderReputation).where(ProviderReputation.provider == provider)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> List[ProviderReputation]:
        result = await self.session.execute(
            select(ProviderReputation).order_by(desc(ProviderReputation.trust_score))
        )
        return list(result.scalars().all())

    async def leaderboard(self, limit: int = 20) -> List[LeaderboardEntry]:
        result = await self.session.execute(
            select(ProviderReputation)
            .order_by(desc(ProviderReputation.trust_score))
            .limit(limit)
        )
        rows = result.scalars().all()
        return [
            LeaderboardEntry(
                rank=i + 1,
                provider=row.provider,
                trust_score=row.trust_score,
                success_rate=row.success_rate,
                rating=row.rating,
                avg_latency=row.avg_latency,
                total_requests=row.total_requests,
            )
            for i, row in enumerate(rows)
        ]

    async def get_breakdown(self, provider: str) -> Optional[TrustScoreBreakdown]:
        record = await self.get_by_provider(provider)
        if record is None:
            return None
        return self.calculator.calculate(
            provider=record.provider,
            success_rate=record.success_rate,
            rating=record.rating,
            avg_latency_ms=record.avg_latency,
            failure_rate=record.failure_rate,
            total_requests=record.total_requests,
        )

    # ------------------------------------------------------------------ #
    # Writes
    # ------------------------------------------------------------------ #

    async def _get_or_create(self, provider: str) -> ProviderReputation:
        record = await self.get_by_provider(provider)
        if record is None:
            record = ProviderReputation(provider=provider)
            self.session.add(record)
            await self.session.flush()
        return record

    async def record_event(self, event: ReputationEventIn) -> ProviderReputation:
        """
        Called by the Execution / Self-Healing modules after each task
        completes (or after a retry/failover). Updates rolling metrics
        and recomputes the composite trust score.
        """
        record = await self._get_or_create(event.provider)

        prior_total = record.total_requests
        new_total = prior_total + 1

        # Rolling average latency
        record.avg_latency = (
            (record.avg_latency * prior_total) + event.latency_ms
        ) / new_total

        # Success / failure counters
        if event.success:
            record.total_successes += 1
        else:
            record.total_failures += 1
        record.total_requests = new_total

        record.success_rate = (record.total_successes / new_total) * 100.0
        record.failure_rate = (record.total_failures / new_total) * 100.0

        # Optional user rating for this execution
        if event.rating is not None:
            record.rating_sum += event.rating
            record.total_ratings += 1
            record.rating = record.rating_sum / record.total_ratings

        # Recompute composite trust score
        breakdown = self.calculator.calculate(
            provider=record.provider,
            success_rate=record.success_rate,
            rating=record.rating,
            avg_latency_ms=record.avg_latency,
            failure_rate=record.failure_rate,
            total_requests=record.total_requests,
        )
        record.trust_score = breakdown.trust_score

        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def reset_provider(self, provider: str) -> Optional[ProviderReputation]:
        """Administrative reset — wipes rolling metrics for a provider."""
        record = await self.get_by_provider(provider)
        if record is None:
            return None
        record.avg_latency = 0.0
        record.success_rate = 0.0
        record.failure_rate = 0.0
        record.rating = 0.0
        record.rating_sum = 0.0
        record.total_requests = 0
        record.total_successes = 0
        record.total_failures = 0
        record.total_ratings = 0
        record.trust_score = 0.0
        await self.session.commit()
        await self.session.refresh(record)
        return record
