from datetime import date

from pydantic import BaseModel


# ---- Cards -----------------------------------------------------------

class DashboardCards(BaseModel):
    total_users: int
    total_requests: int
    revenue: float
    avg_response_time: float | None  # seconds
    popular_provider: str | None
    success_rate: float  # 0-100
    daily_usage: int  # requests today
    monthly_usage: int  # requests this calendar month


# ---- Chart series ------------------------------------------------------

class DateCountPoint(BaseModel):
    date: date
    count: int


class DateValuePoint(BaseModel):
    date: date
    value: float


class ProviderUsagePoint(BaseModel):
    provider: str
    count: int


class SuccessFailurePoint(BaseModel):
    success: int
    failure: int
    success_rate: float  # 0-100


class UserGrowthPoint(BaseModel):
    date: date
    new_users: int
    cumulative_users: int


class DashboardCharts(BaseModel):
    requests_per_day: list[DateCountPoint]
    revenue: list[DateValuePoint]
    provider_usage: list[ProviderUsagePoint]
    response_time: list[DateValuePoint]
    success_vs_failure: SuccessFailurePoint
    user_growth: list[UserGrowthPoint]


class DashboardResponse(BaseModel):
    cards: DashboardCards
    charts: DashboardCharts
    range_days: int
