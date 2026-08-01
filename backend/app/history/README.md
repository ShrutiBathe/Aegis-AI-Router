# Module 6 — History

**Team:** B2 (Service Execution & Marketplace Operations)
**Purpose:** Store every execution — user requests, provider used, prompt/response, cost, and timing.

## Structure

```
history/
├── __init__.py     # exposes `history_router`
├── database.py     # async SQLAlchemy engine/session (swap for shared db module if present)
├── models.py        # `History` SQLAlchemy model
├── schemas.py        # Pydantic request/response schemas
├── service.py        # business logic (create, list, get, delete)
├── router.py          # FastAPI routes
└── README.md
```

## Database schema

| Column       | Type      | Notes                              |
|--------------|-----------|-------------------------------------|
| id           | UUID (PK) | generated on insert                |
| user_id      | string    | indexed                            |
| provider     | string    | indexed (e.g. `openai`, `groq`)    |
| prompt       | text      |                                     |
| response     | text      | nullable (e.g. failed execution)   |
| cost         | float     | in whatever unit Payment settles in |
| time_taken   | float     | seconds, nullable                  |
| created_at   | timestamp | server-set default, indexed        |

A composite index on `(user_id, created_at)` supports the common "recent history for this user" query pattern.

## API

| Method | Path              | Description                                       |
|--------|-------------------|----------------------------------------------------|
| GET    | `/history`        | List history, newest first. Query params: `user_id`, `provider`, `limit` (default 50, max 200), `offset`. |
| GET    | `/history/{id}`   | Fetch a single record.                             |
| DELETE | `/history/{id}`   | Delete a record by ID. Returns 404 if not found.   |

Writes are **not** exposed over the API — records are created internally by the Execution module via `HistoryService.create()` once a task finishes (success or failure), so the history log stays an accurate append-only record of what actually ran.

## Wiring into the app

```python
# main.py (or wherever the FastAPI app is assembled)
from history import history_router

app.include_router(history_router)
```

## Integration point for Execution module

```python
from history.schemas import HistoryCreate
from history.service import HistoryService

await HistoryService.create(
    db,
    HistoryCreate(
        user_id=user_id,
        provider=provider_name,
        prompt=prompt,
        response=result_text,
        cost=cost,
        time_taken=elapsed_seconds,
    ),
)
```

## Open items / assumptions to confirm with the team

- `database.py` here is standalone. If a shared `db.py`/`database.py` already exists (used by Payment, Execution, etc.), delete this file and import `Base` + `get_db` from there instead — history should share the platform's engine.
- `user_id` is stored as a plain string, not a foreign key, so this module has zero dependency on the Auth/User module's shape. Add a `ForeignKey` once that table's name/type is settled.
- No auth/ownership check on `GET`/`DELETE` yet — as written, any caller can read or delete any record. Add a dependency that scopes queries to the authenticated user's own `user_id` before this goes past internal testing.
- Pagination + provider filter on `GET /history` were added beyond the original spec (2 endpoints) since the table will grow quickly in a marketplace context — drop them if you want the bare `GET`/`DELETE` only.
