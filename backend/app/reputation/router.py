"""
router.py — FastAPI endpoints for the Reputation module.

Mount in the main app with:

    from reputation import reputation_router
    app.include_router(reputation_router)
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import (
    ProviderReputationRead,
    ReputationEventIn,
    TrustScoreBreakdownOut,
    LeaderboardEntry,
)
from .service import ReputationService

# Replace with your app's actual DB session dependency
from .db import get_session  # see db.py

router = APIRouter(prefix="/reputation", tags=["Reputation"])


def get_service(session: AsyncSession = Depends(get_session)) -> ReputationService:
    return ReputationService(session)


@router.post(
    "/events",
    response_model=ProviderReputationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest an execution event and update the provider's trust score",
)
async def ingest_event(
    event: ReputationEventIn,
    service: ReputationService = Depends(get_service),
):
    """
    Called internally by the Execution and Self-Healing modules after
    every task attempt (including retries/failovers) so the Reputation
    System stays in sync with real marketplace activity.
    """
    record = await service.record_event(event)
    return record


@router.get(
    "/providers/{provider}",
    response_model=ProviderReputationRead,
    summary="Get the current reputation record for a provider",
)
async def get_provider_reputation(
    provider: str,
    service: ReputationService = Depends(get_service),
):
    record = await service.get_by_provider(provider)
    if record is None:
        raise HTTPException(status_code=404, detail=f"No reputation record for '{provider}'")
    return record


@router.get(
    "/providers/{provider}/breakdown",
    response_model=TrustScoreBreakdownOut,
    summary="Get a transparent breakdown of how a provider's trust score was computed",
)
async def get_provider_breakdown(
    provider: str,
    service: ReputationService = Depends(get_service),
):
    breakdown = await service.get_breakdown(provider)
    if breakdown is None:
        raise HTTPException(status_code=404, detail=f"No reputation record for '{provider}'")
    return TrustScoreBreakdownOut(**breakdown.__dict__)


@router.get(
    "/providers",
    response_model=List[ProviderReputationRead],
    summary="List reputation records for all providers, ranked by trust score",
)
async def list_providers(service: ReputationService = Depends(get_service)):
    return await service.list_all()


@router.get(
    "/leaderboard",
    response_model=List[LeaderboardEntry],
    summary="Top-ranked providers by trust score (used by the Router module)",
)
async def leaderboard(
    limit: int = 20,
    service: ReputationService = Depends(get_service),
):
    return await service.leaderboard(limit=limit)


@router.post(
    "/providers/{provider}/reset",
    response_model=ProviderReputationRead,
    summary="Admin: reset a provider's rolling metrics and trust score",
)
async def reset_provider(
    provider: str,
    service: ReputationService = Depends(get_service),
):
    record = await service.reset_provider(provider)
    if record is None:
        raise HTTPException(status_code=404, detail=f"No reputation record for '{provider}'")
    return record
