"""
scoring.py — Trust Score Calculator

    Trust Score = 40% Success + 30% Rating + 20% Speed + 10% Reliability

All four components are normalized to a 0-100 scale before weighting so the
final trust_score is always in [0, 100].

- Success component  : success_rate, already 0-100 (%).
- Rating component    : user rating 0-5 stars, scaled to 0-100.
- Speed component     : avg_latency (ms), inverted and normalized against a
                         configurable "acceptable" latency ceiling — faster
                         responses score higher.
- Reliability component: derived from failure_rate and request volume, so
                         a provider with very few requests (low confidence)
                         or a high failure_rate scores lower.
"""

from dataclasses import dataclass, field
from typing import Dict

# Weights per the Module 5 spec
WEIGHT_SUCCESS = 0.40
WEIGHT_RATING = 0.30
WEIGHT_SPEED = 0.20
WEIGHT_RELIABILITY = 0.10

# Latency ceiling (ms) beyond which speed score bottoms out at 0.
# Tuneable per deployment / SLA tier.
DEFAULT_LATENCY_CEILING_MS = 5000.0

# Requests below this volume get a confidence discount applied to
# the reliability component (new/unproven providers shouldn't
# instantly rank alongside established ones).
MIN_CONFIDENT_REQUESTS = 20


@dataclass
class TrustScoreBreakdown:
    provider: str
    trust_score: float
    success_component: float
    rating_component: float
    speed_component: float
    reliability_component: float
    weights: Dict[str, float] = field(
        default_factory=lambda: {
            "success": WEIGHT_SUCCESS,
            "rating": WEIGHT_RATING,
            "speed": WEIGHT_SPEED,
            "reliability": WEIGHT_RELIABILITY,
        }
    )


class TrustScoreCalculator:
    """Stateless calculator — pure functions over raw metrics."""

    def __init__(self, latency_ceiling_ms: float = DEFAULT_LATENCY_CEILING_MS):
        self.latency_ceiling_ms = latency_ceiling_ms

    def _speed_score(self, avg_latency_ms: float) -> float:
        """Lower latency -> higher score. Clamped to [0, 100]."""
        if avg_latency_ms <= 0:
            return 100.0
        score = 100.0 * (1 - (avg_latency_ms / self.latency_ceiling_ms))
        return max(0.0, min(100.0, score))

    def _reliability_score(
        self, failure_rate: float, total_requests: int
    ) -> float:
        """
        Base reliability = 100 - failure_rate (both on 0-100 scale).
        Apply a confidence discount for low-volume providers so a
        provider with 1 lucky success doesn't outrank one with 500
        consistent successes.
        """
        base = max(0.0, min(100.0, 100.0 - failure_rate))
        if total_requests >= MIN_CONFIDENT_REQUESTS:
            confidence = 1.0
        else:
            confidence = total_requests / MIN_CONFIDENT_REQUESTS
        return base * confidence

    def calculate(
        self,
        provider: str,
        success_rate: float,
        rating: float,
        avg_latency_ms: float,
        failure_rate: float,
        total_requests: int,
    ) -> TrustScoreBreakdown:
        success_component = max(0.0, min(100.0, success_rate))
        rating_component = max(0.0, min(100.0, (rating / 5.0) * 100.0))
        speed_component = self._speed_score(avg_latency_ms)
        reliability_component = self._reliability_score(failure_rate, total_requests)

        trust_score = (
            WEIGHT_SUCCESS * success_component
            + WEIGHT_RATING * rating_component
            + WEIGHT_SPEED * speed_component
            + WEIGHT_RELIABILITY * reliability_component
        )

        return TrustScoreBreakdown(
            provider=provider,
            trust_score=round(trust_score, 2),
            success_component=round(success_component, 2),
            rating_component=round(rating_component, 2),
            speed_component=round(speed_component, 2),
            reliability_component=round(reliability_component, 2),
        )
