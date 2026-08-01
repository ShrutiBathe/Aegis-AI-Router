from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import DashboardResponse
from .service import AnalyticsService


async def build_dashboard(db: AsyncSession, days: int = 30) -> DashboardResponse:
    """
    Assembles the full dashboard payload (all 8 cards + all 6 charts) in
    one call so the frontend can render the page with a single request.

    `days` controls the window for the *charts* only — the cards are
    mostly all-time totals (total_users, total_requests, revenue) except
    for daily_usage/monthly_usage, which are always "today" / "this
    calendar month" regardless of `days`.
    """
    cards = await AnalyticsService.get_cards(db)
    charts = await AnalyticsService.get_charts(db, days=days)
    return DashboardResponse(cards=cards, charts=charts, range_days=days)
