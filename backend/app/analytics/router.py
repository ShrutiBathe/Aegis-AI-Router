from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.history.database import get_db

from .dashboard import build_dashboard
from .schemas import (
    DashboardCards,
    DashboardResponse,
    DateCountPoint,
    DateValuePoint,
    ProviderUsagePoint,
    SuccessFailurePoint,
    UserGrowthPoint,
)
from .service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])

DaysParam = Query(default=30, ge=1, le=365, description="Window size in days for chart data")


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(days: int = DaysParam, db: AsyncSession = Depends(get_db)) -> DashboardResponse:
    """Full dashboard payload: all 8 cards + all 6 charts in one call."""
    return await build_dashboard(db, days=days)


@router.get("/cards", response_model=DashboardCards)
async def get_cards(db: AsyncSession = Depends(get_db)) -> DashboardCards:
    """Just the summary cards, for a lighter-weight poll/refresh."""
    return await AnalyticsService.get_cards(db)


@router.get("/charts/requests-per-day", response_model=list[DateCountPoint])
async def get_requests_per_day(days: int = DaysParam, db: AsyncSession = Depends(get_db)):
    return await AnalyticsService.get_requests_per_day(db, days=days)


@router.get("/charts/revenue", response_model=list[DateValuePoint])
async def get_revenue_chart(days: int = DaysParam, db: AsyncSession = Depends(get_db)):
    return await AnalyticsService.get_revenue_chart(db, days=days)


@router.get("/charts/provider-usage", response_model=list[ProviderUsagePoint])
async def get_provider_usage(days: int = DaysParam, db: AsyncSession = Depends(get_db)):
    return await AnalyticsService.get_provider_usage(db, days=days)


@router.get("/charts/response-time", response_model=list[DateValuePoint])
async def get_response_time_chart(days: int = DaysParam, db: AsyncSession = Depends(get_db)):
    return await AnalyticsService.get_response_time_chart(db, days=days)


@router.get("/charts/success-failure", response_model=SuccessFailurePoint)
async def get_success_vs_failure(days: int = DaysParam, db: AsyncSession = Depends(get_db)):
    return await AnalyticsService.get_success_vs_failure(db, days=days)


@router.get("/charts/user-growth", response_model=list[UserGrowthPoint])
async def get_user_growth(days: int = DaysParam, db: AsyncSession = Depends(get_db)):
    return await AnalyticsService.get_user_growth(db, days=days)
