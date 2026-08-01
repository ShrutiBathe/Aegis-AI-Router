# Aegis AI Router — Team B2 Integration Notes

How to run the fully-wired app:

```
uvicorn app.main:app --reload
```
(run from the directory *containing* `app/`, matching the `app.<module>` import
convention already used by `main_test.py` and `payments/router.py`.)

Env vars: `DATABASE_URL` (async, e.g. `postgresql+asyncpg://...`) drives History/
Reputation/Analytics. `SYNC_DATABASE_URL` (optional override; else derived from
`DATABASE_URL`) drives Payment. Per-provider API keys: `OPENAI_API_KEY`,
`ANTHROPIC_API_KEY` (claude), `GEMINI_API_KEY`, `GROQ_API_KEY` — ollama needs none.

## New files

| File | Purpose |
|---|---|
| `app/__init__.py` | Makes `app` a real package (was missing) |
| `app/main.py` | Real entrypoint — mounts every router, runs sync + async table creation on startup |
| `app/database/base.py` | Shared sync declarative `Base` (Payment) |
| `app/database/session.py` | Shared sync engine/session + `get_db` (Payment) |
| `app/database/async_db.py` | Shared async engine/session + `get_async_db` (History/Reputation/Analytics) |
| `app/database/stub_models.py` | Placeholder `users`/`agents`/`tasks` tables so Payment's FKs resolve — **delete once Auth/Marketplace modules exist** |
| `app/core/deps.py` | Placeholder `get_current_user` (reads `X-User-Id` header) — **replace with real Auth module** |
| `app/ai_integrations/registry.py` | Bridges `ai_integrations.factory` to the `provider_registry` protocol `self_healing` already expected |
| `app/orchestrator/` (schemas/service/router) | The master workflow (integration rule #12) |
| `app/payments/__init__.py` | Was missing; exposes `payment_router`, `wallet_router` |

## Modified files (and why)

| File | Change |
|---|---|
| `self_healing/provider_interface.py` | Fixed import path (`ai_integrations.registry` → `app.ai_integrations.registry`) — it was silently falling back to a fake in-memory provider on every request |
| `analytics/service.py` | Fixed absolute import (`history.models` → `app.history.models`); added `record_success`/`record_failure` logging hooks |
| `analytics/router.py` | Fixed absolute import (`history.database` → `app.history.database`) |
| `history/models.py`, `schemas.py`, `service.py` | Added `status`, `request_id`, `retries`, `payment_id` fields the integration spec requires |
| `history/database.py` | Re-points at the shared async engine instead of rolling its own |
| `reputation/db.py` | Re-points at the shared async engine instead of a different default database (`aegis_reputation` → shared `aegis_router`) |
| `payments/test_payment_flow.py` | Fixed stale package name (`payment_module` → `app.payments`) so this pre-existing test actually runs |

## Deleted

- `analytics/models.py` — dead duplicate `History` model, imported a nonexistent `analytics/database.py`, never referenced by anything
- `analytics/mnt/` — stray artifact directory, not part of the module

## Deliberately NOT touched

- `execution/service.py`, `executor.py`, `queue.py` — left mounted standalone at `POST /execute` for isolated testing of that module. Its Executor+fire-and-forget-queue design has no way to feed a self-healing result back into the original HTTP response, so it isn't part of the orchestrated flow — `self_healing.execute_task()` already implements the "call provider → retry → switch → retry → exhaust" sequence rule #5 describes, so the orchestrator calls that directly.
- `execution/router.py` still creates its own local `sqlite:///./execution_engine.db` at import time. Harmless, but means `/execute` runs against a different database than everything else. Left as-is since fixing it means editing that module's own business logic.
- All provider clients in `ai_integrations/` (openai.py, claude.py, etc.) and all of `self_healing`'s retry/circuit-breaker/failover logic — untouched, only *wired to*.

## Known simplifications (flagged, not hidden)

- **Payment `agent_id`** is a UUID FK to a real Agents table that doesn't exist yet. `orchestrator/service.py:provider_to_agent_id()` derives a stable UUID5 from the provider name as a stand-in.
- **Cost is charged against the primary candidate provider**, not the eventual winner — acceptable today since `PaymentService.estimate_cost()` already ignores `agent_id` for pricing (flat rate, per its own TODO comment).
- **Reputation on full failure** splits `total_duration_ms` evenly across attempted providers, since `TaskResult` doesn't expose per-provider latency on the all-failed path (only on success). Finer-grained data exists inside `self_healing`'s `_emit()` events if this needs tightening later.
- **No auth** beyond the `X-User-Id` header stub — replace `app/core/deps.py` wholesale once a real Auth module exists.
