# Module 7 — Analytics Dashboard

**Team:** B2 (Service Execution & Marketplace Operations)
**Purpose:** Show platform statistics — summary cards + charts, aggregated from execution history.

## Structure

```
analytics/
├── __init__.py     # exposes `analytics_router`
├── schemas.py        # Pydantic response models (cards, chart points, full dashboard)
├── service.py         # aggregation queries, one method per stat/chart
├── router.py            # FastAPI routes
├── dashboard.py          # composes cards + charts into one payload
└── README.md
```

No `models.py` — this module owns no tables. It's a read-only aggregation layer over the `history` table from **Module 6**.

## Dashboard cards

| Card               | Source                                               |
|---------------------|--------------------------------------------------------|
| Total Users          | `COUNT(DISTINCT user_id)` in `history`                |
| Total Requests        | `COUNT(*)` in `history`                                |
| Revenue                | `SUM(cost)` in `history`                                |
| Average Response Time    | `AVG(time_taken)` in `history`                          |
| Popular Provider          | provider with the highest request count                 |
| Success Rate                | `%` of rows with `status = success`                      |
| Daily Usage                    | request count for today (UTC)                             |
| Monthly Usage                    | request count for the current calendar month (UTC)          |

## Charts

| Chart               | Endpoint                              | Notes |
|-----------------------|-----------------------------------------|-------|
| Requests per Day        | `GET /analytics/charts/requests-per-day`  | grouped by day |
| Revenue                    | `GET /analytics/charts/revenue`             | summed cost per day |
| Provider Usage                | `GET /analytics/charts/provider-usage`        | request count per provider |
| Response Time                    | `GET /analytics/charts/response-time`           | avg `time_taken` per day |
| Success vs Failure                  | `GET /analytics/charts/success-failure`           | single object, not a series |
| User Growth                            | `GET /analytics/charts/user-growth`                 | new users per day + running total |

All chart endpoints take an optional `?days=N` query param (default 30, max 365).

## API summary

| Method | Path                                    | Description                             |
|--------|-------------------------------------------|-------------------------------------------|
| GET    | `/analytics/dashboard?days=30`               | Full payload: all cards + all charts, one call |
| GET    | `/analytics/cards`                              | Just the 8 summary cards                  |
| GET    | `/analytics/charts/{name}?days=30`                | Individual chart data (6 routes, see table above) |

## Wiring into the app

```python
from analytics import analytics_router
app.include_router(analytics_router)
```

This module imports `History` and `get_db` directly from the `history` package (`from history.models import ...`, `from history.database import get_db`), so `history/` needs to be importable alongside it — same parent package, or installed as a shared dependency.

## Changes made to Module 6 (History) to support this module

Success Rate and Success vs Failure need to know whether an execution succeeded. The original History model didn't track that, so `history/models.py` now has a `status` column (`ExecutionStatus`: `success` / `failure`, defaults to `success`), propagated through `schemas.py` and `service.py`. If you already added a status/result field to History independently, reconcile the enum names before merging.

## Open items / assumptions to confirm with the team

- **Revenue** sums `history.cost`. If the Payment module's transactions table is the source of truth (e.g. it accounts for refunds, failed charges, or different pricing than what's logged at execution time), point `get_revenue()` / `get_revenue_chart()` at that table instead.
- **Total Users** and **User Growth** are both derived from `history.user_id` (distinct users who've made a request, and each user's first request date as a proxy for "new user"). If there's a real Users/Auth table with actual signup timestamps, swap these two to query that instead — it'll be more accurate than the History-based proxy.
- All aggregation queries use plain `func.date(...)` / UTC `datetime.now()`, which assumes Postgres. If the DB is something else, the date-grouping calls in `service.py` may need adjusting.
- No caching — every dashboard load recomputes all 8 cards + 6 charts (14 queries) live. Fine for now; worth adding a short TTL cache (Redis or in-process) once traffic grows, since none of these numbers need to be real-time-fresh.
- No auth on these routes yet, same as History — analytics data is presumably admin/internal-only, so this should sit behind whatever admin-auth dependency the platform uses before shipping.
