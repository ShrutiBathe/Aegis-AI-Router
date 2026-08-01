# Module 5 — Reputation System

**Team B2: Service Execution & Marketplace Operations — Aegis AI Router**

Maintains a live trust score for every AI provider/agent registered in the
marketplace (OpenAI, Gemini, Claude, Groq, Ollama, etc.), so the Router
module can rank and route requests to the most reliable, well-performing,
best-rated agents.

## Purpose

Every time the Execution module (or the Self-Healing module, on retry/
failover) completes a task against a provider, it emits an event to this
module. The Reputation System updates that provider's rolling metrics and
recomputes a composite **Trust Score**.

## Metrics tracked

| Metric | Description |
|---|---|
| Success Rate | % of requests that completed successfully |
| Average Response Time | Rolling average latency (ms) |
| User Rating | Rolling average of 0–5 star ratings, when supplied |
| Failure Rate | % of requests that failed |
| Total Requests | Volume counter, used for confidence weighting |

## Trust Score formula

```
Trust Score = 40% Success + 30% Rating + 20% Speed + 10% Reliability
```

All four components are normalized to 0–100 before weighting:

- **Success** — `success_rate`, already 0–100.
- **Rating** — user rating (0–5) scaled to 0–100.
- **Speed** — inverse of average latency, normalized against a configurable
  latency ceiling (default 5000ms). Faster = higher score.
- **Reliability** — `100 - failure_rate`, discounted by a confidence factor
  for providers with fewer than 20 total requests, so unproven agents don't
  outrank established ones on a small sample.

See [`scoring.py`](./scoring.py) for the implementation and tunables.

## Database schema — `provider_reputation`

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| provider | string | Unique provider identifier, e.g. `openai:gpt-4o` |
| trust_score | float | Computed composite score (0–100) |
| avg_latency | float | Rolling average latency (ms) |
| success_rate | float | 0–100 (%) |
| failure_rate | float | 0–100 (%) |
| rating | float | Rolling average user rating (0–5) |
| total_requests | int | Lifetime request count |
| total_successes | int | Lifetime success count |
| total_failures | int | Lifetime failure count |
| total_ratings | int | Number of ratings received |
| rating_sum | float | Sum of all ratings (for rolling average) |
| created_at | timestamp | |
| updated_at | timestamp | |

## File structure

```
reputation/
├── __init__.py     # Public exports
├── models.py        # SQLAlchemy ORM model (provider_reputation table)
├── schemas.py        # Pydantic request/response schemas
├── scoring.py        # TrustScoreCalculator — implements the weighted formula
├── service.py         # Business logic: ingest events, compute/query scores
├── router.py           # FastAPI endpoints
├── db.py                # Async engine/session setup (swap in shared DB config)
└── README.md
```

## API

All endpoints are mounted under `/reputation`.

| Method | Path | Description |
|---|---|---|
| POST | `/reputation/events` | Ingest an execution event (called by Execution / Self-Healing) |
| GET | `/reputation/providers/{provider}` | Get a provider's current reputation record |
| GET | `/reputation/providers/{provider}/breakdown` | Get the component-level trust score breakdown |
| GET | `/reputation/providers` | List all providers, ranked by trust score |
| GET | `/reputation/leaderboard?limit=20` | Top-ranked providers (used by the Router module) |
| POST | `/reputation/providers/{provider}/reset` | Admin: reset a provider's rolling metrics |

### Example: recording an execution event

```json
POST /reputation/events
{
  "provider": "groq:llama-3.1-70b",
  "success": true,
  "latency_ms": 420,
  "rating": 4.5
}
```

Response — updated `ProviderReputationRead`:

```json
{
  "provider": "groq:llama-3.1-70b",
  "trust_score": 87.32,
  "avg_latency": 420.0,
  "success_rate": 100.0,
  "failure_rate": 0.0,
  "rating": 4.5,
  "total_requests": 1,
  ...
}
```

## Integration points

- **Execution module**: calls `POST /reputation/events` after every task
  attempt.
- **Self-Healing module**: calls the same endpoint after retries/failovers
  so failed attempts are reflected in `failure_rate` before switching to a
  backup agent.
- **Router module**: reads `GET /reputation/leaderboard` (or queries
  `ReputationService.leaderboard()` directly in-process) to weight routing
  decisions toward higher trust-score providers.
- **Analytics module**: can query `GET /reputation/providers` for dashboard
  aggregation.

## Wiring it up

```python
from fastapi import FastAPI
from reputation import reputation_router
from reputation.db import init_db

app = FastAPI()
app.include_router(reputation_router)

@app.on_event("startup")
async def on_startup():
    await init_db()
```

Set `REPUTATION_DATABASE_URL` (or point `db.py` at the shared Aegis AI
Router database used by the other B2 modules) before running in production,
and prefer Alembic migrations over `init_db()`'s `create_all` for schema
management.

## Notes / tunables

- `DEFAULT_LATENCY_CEILING_MS` (in `scoring.py`) — latency beyond which the
  speed component bottoms out at 0. Tune per SLA tier.
- `MIN_CONFIDENT_REQUESTS` (in `scoring.py`) — request volume threshold
  below which the reliability component is confidence-discounted.
- Weights (`WEIGHT_SUCCESS`, `WEIGHT_RATING`, `WEIGHT_SPEED`,
  `WEIGHT_RELIABILITY`) are centralized constants in `scoring.py` if the
  40/30/20/10 split ever needs to change.
