import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.history.models import ExecutionStatus, History

logger = logging.getLogger("analytics.service")

from .schemas import (
    DashboardCards,
    DashboardCharts,
    DateCountPoint,
    DateValuePoint,
    ProviderUsagePoint,
    SuccessFailurePoint,
    UserGrowthPoint,
)


def _range_start(days: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days)


class AnalyticsService:
    """Read-only aggregation over the `history` table."""

    # ---- Cards ---------------------------------------------------------

    @staticmethod
    async def get_total_users(db: AsyncSession) -> int:
        result = await db.execute(select(func.count(func.distinct(History.user_id))))
        return result.scalar_one() or 0

    @staticmethod
    async def get_total_requests(db: AsyncSession) -> int:
        result = await db.execute(select(func.count()).select_from(History))
        return result.scalar_one() or 0

    @staticmethod
    async def get_revenue(db: AsyncSession) -> float:
        result = await db.execute(select(func.coalesce(func.sum(History.cost), 0.0)))
        return float(result.scalar_one() or 0.0)

    @staticmethod
    async def get_avg_response_time(db: AsyncSession) -> float | None:
        result = await db.execute(select(func.avg(History.time_taken)))
        value = result.scalar_one()
        return float(value) if value is not None else None

    @staticmethod
    async def get_popular_provider(db: AsyncSession) -> str | None:
        result = await db.execute(
            select(History.provider, func.count().label("cnt"))
            .group_by(History.provider)
            .order_by(func.count().desc())
            .limit(1)
        )
        row = result.first()
        return row[0] if row else None

    @staticmethod
    async def get_success_rate(db: AsyncSession) -> float:
        result = await db.execute(
            select(
                func.count().label("total"),
                func.sum(
                    case((History.status == ExecutionStatus.SUCCESS, 1), else_=0)
                ).label("successes"),
            )
        )
        total, successes = result.first()
        if not total:
            return 0.0
        return round((successes or 0) / total * 100, 2)

    @staticmethod
    async def get_daily_usage(db: AsyncSession) -> int:
        today = datetime.now(timezone.utc).date()
        result = await db.execute(
            select(func.count()).where(func.date(History.created_at) == today)
        )
        return result.scalar_one() or 0

    @staticmethod
    async def get_monthly_usage(db: AsyncSession) -> int:
        now = datetime.now(timezone.utc)
        month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        result = await db.execute(
            select(func.count()).where(History.created_at >= month_start)
        )
        return result.scalar_one() or 0

    @staticmethod
    async def get_cards(db: AsyncSession) -> DashboardCards:
        return DashboardCards(
            total_users=await AnalyticsService.get_total_users(db),
            total_requests=await AnalyticsService.get_total_requests(db),
            revenue=await AnalyticsService.get_revenue(db),
            avg_response_time=await AnalyticsService.get_avg_response_time(db),
            popular_provider=await AnalyticsService.get_popular_provider(db),
            success_rate=await AnalyticsService.get_success_rate(db),
            daily_usage=await AnalyticsService.get_daily_usage(db),
            monthly_usage=await AnalyticsService.get_monthly_usage(db),
        )

    # ---- Charts ----------------------------------------------------------

    @staticmethod
    async def get_requests_per_day(db: AsyncSession, days: int = 30) -> list[DateCountPoint]:
        day_col = func.date(History.created_at).label("day")
        result = await db.execute(
            select(day_col, func.count().label("count"))
            .where(History.created_at >= _range_start(days))
            .group_by(day_col)
            .order_by(day_col)
        )
        return [DateCountPoint(date=row.day, count=row.count) for row in result.all()]

    @staticmethod
    async def get_revenue_chart(db: AsyncSession, days: int = 30) -> list[DateValuePoint]:
        day_col = func.date(History.created_at).label("day")
        result = await db.execute(
            select(day_col, func.coalesce(func.sum(History.cost), 0.0).label("total"))
            .where(History.created_at >= _range_start(days))
            .group_by(day_col)
            .order_by(day_col)
        )
        return [DateValuePoint(date=row.day, value=float(row.total)) for row in result.all()]

    @staticmethod
    async def get_provider_usage(db: AsyncSession, days: int = 30) -> list[ProviderUsagePoint]:
        result = await db.execute(
            select(History.provider, func.count().label("count"))
            .where(History.created_at >= _range_start(days))
            .group_by(History.provider)
            .order_by(func.count().desc())
        )
        return [ProviderUsagePoint(provider=row.provider, count=row.count) for row in result.all()]

    @staticmethod
    async def get_response_time_chart(db: AsyncSession, days: int = 30) -> list[DateValuePoint]:
        day_col = func.date(History.created_at).label("day")
        result = await db.execute(
            select(day_col, func.avg(History.time_taken).label("avg_time"))
            .where(History.created_at >= _range_start(days))
            .group_by(day_col)
            .order_by(day_col)
        )
        return [
            DateValuePoint(date=row.day, value=float(row.avg_time or 0.0))
            for row in result.all()
        ]

    @staticmethod
    async def get_success_vs_failure(db: AsyncSession, days: int = 30) -> SuccessFailurePoint:
        result = await db.execute(
            select(
                func.sum(
                    case((History.status == ExecutionStatus.SUCCESS, 1), else_=0)
                ).label("successes"),
                func.sum(
                    case((History.status == ExecutionStatus.FAILURE, 1), else_=0)
                ).label("failures"),
            ).where(History.created_at >= _range_start(days))
        )
        successes, failures = result.first()
        successes, failures = successes or 0, failures or 0
        total = successes + failures
        rate = round(successes / total * 100, 2) if total else 0.0
        return SuccessFailurePoint(success=successes, failure=failures, success_rate=rate)

    @staticmethod
    async def get_user_growth(db: AsyncSession, days: int = 30) -> list[UserGrowthPoint]:
        """
        New users per day, based on each user's first-ever History row.
        NOTE: this is a proxy for "first request", not "account created" —
        see README open items if a dedicated Users table with signup
        timestamps exists elsewhere in the platform.
        """
        first_seen_subq = (
            select(
                History.user_id,
                func.min(func.date(History.created_at)).label("first_day"),
            )
            .group_by(History.user_id)
            .subquery()
        )

        result = await db.execute(
            select(
                first_seen_subq.c.first_day,
                func.count().label("new_users"),
            )
            .where(first_seen_subq.c.first_day >= _range_start(days).date())
            .group_by(first_seen_subq.c.first_day)
            .order_by(first_seen_subq.c.first_day)
        )
        rows = result.all()

        # Running cumulative total across the returned window.
        cumulative = 0
        points: list[UserGrowthPoint] = []
        for row in rows:
            cumulative += row.new_users
            points.append(
                UserGrowthPoint(
                    date=row.first_day, new_users=row.new_users, cumulative_users=cumulative
                )
            )
        return points

    @staticmethod
    async def get_charts(db: AsyncSession, days: int = 30) -> DashboardCharts:
        return DashboardCharts(
            requests_per_day=await AnalyticsService.get_requests_per_day(db, days),
            revenue=await AnalyticsService.get_revenue_chart(db, days),
            provider_usage=await AnalyticsService.get_provider_usage(db, days),
            response_time=await AnalyticsService.get_response_time_chart(db, days),
            success_vs_failure=await AnalyticsService.get_success_vs_failure(db, days),
            user_growth=await AnalyticsService.get_user_growth(db, days),
        )

    # ---- Write-side hooks (integration) ---------------------------------
    #
    # AnalyticsService is intentionally read-only: every card/chart above
    # is derived live from the `history` table, so anything HistoryService
    # writes is already reflected here on the next read — there's no
    # separate counters table that could drift out of sync with History.
    #
    # The integration spec still calls for the orchestrator to notify
    # Analytics after every request (`AnalyticsService.record_success` /
    # `record_failure`), so these exist as the call target — today they
    # just log; they're the seam to add real-time counters (e.g. a Redis
    # gauge for a live-updating dashboard) later without touching the
    # orchestrator's call site.

    @staticmethod
    async def record_success(
        provider: str, cost: float, time_taken: float | None, retries: int = 0
    ) -> None:
        logger.info(
            "analytics: success provider=%s cost=%.4f time_taken=%s retries=%d",
            provider, cost, time_taken, retries,
        )

    @staticmethod
    async def record_failure(
        provider: str | None, retries: int = 0, error: str | None = None
    ) -> None:
        logger.info(
            "analytics: failure provider=%s retries=%d error=%s", provider, retries, error
        )
