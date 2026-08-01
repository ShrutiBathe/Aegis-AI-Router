# Module 2 — Execution Engine

Executes a request against a selected AI agent, persists the outcome, and
hands failed executions off to Self-Healing. This is the piece that sits
between the router (Module 1's "Selected AI Agent" step) and the
AI Integration Layer.

## Flow

```
Receive Agent
      │
      ▼
Validate Request
      │
      ▼
Call AI Integration
      │
      ▼
Receive Response
      │
      ▼
Return Response
      │
      ▼ (only if execution fails)
Self-Healing
```

## API

```
POST /execute
```

Request:

```json
{
  "agent": "OpenAI",
  "prompt": "Explain AI Routing"
}
```

Response (success):

```json
{
  "id": "7a260707-19da-4def-a7f9-ec27f6f13c8d",
  "agent": "OpenAI",
  "status": "success",
  "response": "Echo: Explain AI Routing",
  "error": null,
  "latency_ms": 10.35,
  "retries": 0,
  "created_at": "2026-07-31T16:23:04.880118"
}
```

Response (failure — still HTTP 200, since the request itself was valid and
was recorded; the *execution* failed):

```json
{
  "id": "b70190f1-e0b3-4020-a068-e551b9a88842",
  "agent": "Anthropic",
  "status": "failed",
  "response": null,
  "error": "upstream 503",
  "latency_ms": 10.72,
  "retries": 1,
  "created_at": "2026-07-31T16:23:16.701843"
}
```

```
GET /execute/{id}
```

Looks up a past execution by id (used by History/Analytics/Reputation).

Optional request field:

- `params` — dict of agent-specific parameters (`temperature`, `max_tokens`, ...), passed through untouched to the AI Integration client.
- `request_id` — client-supplied idempotency key. If the same `request_id` is replayed and the original execution succeeded, the cached record is returned instead of re-executing.

## Files

| File | Responsibility |
|---|---|
| `models.py` | SQLAlchemy `ExecutionRecord` — the persisted row for every execute call (agent, prompt, response, status, error, latency, retries). |
| `schemas.py` | Pydantic `ExecuteRequest` / `ExecuteResponse` / `ExecutionRecordOut` — the public wire format, decoupled from the DB schema. |
| `executor.py` | `Executor` — calls the AI Integration Layer with a timeout and bounded retry-with-backoff. Adapters implement the `AIIntegrationClient` protocol and are registered by agent name. Never raises to callers except `AgentNotSupportedError`. |
| `service.py` | `ExecutionEngineService` — orchestrates validate → execute → persist → (on failure) enqueue self-healing. The only class `router.py` talks to. |
| `router.py` | FastAPI routes: `POST /execute`, `GET /execute/{id}`. Owns a default SQLite session factory and an `Executor`/`InMemorySelfHealingQueue` singleton for standalone use. |
| `queue.py` | `SelfHealingQueue` protocol + `InMemorySelfHealingQueue` — dispatches failed executions to a handler owned by the Self-Healing module. Swappable for Celery/SQS/Kafka. |

## Design notes

- **executor.py never touches the DB or HTTP.** It only knows how to call an `AIIntegrationClient` and how to behave when that call times out or throws. This keeps it independently testable and lets the AI Integration Layer evolve without touching persistence or routing.
- **Validation failures are still persisted.** An unsupported agent or an over-length prompt is recorded as a `failed` execution rather than just a 4xx response, so History/Analytics see a complete audit trail, including rejected requests. Genuinely malformed JSON (e.g. an empty `prompt` string) is rejected by Pydantic before it reaches the service, and returns a normal `422`.
- **Self-Healing is fire-and-forget from the Execution Engine's point of view.** `service.py` enqueues a `SelfHealingTask` and moves on; it does not wait for or depend on the outcome of healing.
- **Retries live in `executor.py`, not in the queue.** A configurable number of in-process retries with backoff happen *before* a result is considered a failure; only after those are exhausted does the failure get recorded and handed to Self-Healing.
- **Idempotency** is opportunistic: pass a `request_id` (e.g. per-user request UUID) to get replay-safe behavior on retried client calls.

## Wiring it up for real

`router.py` ships with a working SQLite engine and an `Executor` with no
registered agents, so the module runs standalone out of the box. To connect
it to real AI providers, register clients where `_service_singleton()` is
defined (or override it entirely from your app's `main.py`):

```python
from module2.executor import Executor
from module2.queue import InMemorySelfHealingQueue
from module2.service import ExecutionEngineService

executor = Executor(timeout_seconds=15, max_retries=2)
executor.register_client("openai", OpenAIIntegrationClient(api_key=...))
executor.register_client("anthropic", AnthropicIntegrationClient(api_key=...))

service = ExecutionEngineService(executor=executor, self_healing_queue=InMemorySelfHealingQueue())
```

And to actually process self-healing tasks, start the queue's worker with a
handler from the Self-Healing module during app startup:

```python
@app.on_event("startup")
async def start_self_healing_worker():
    service.self_healing_queue.start_worker(self_healing_module.handle_task)
```

## Adding a new agent

1. Implement `AIIntegrationClient` (an async `call(prompt, params) -> str`) in the AI Integration Layer.
2. Add the agent's lowercase name to `SUPPORTED_AGENTS` in `service.py`.
3. Register it: `executor.register_client("newagent", NewAgentClient(...))`.

## Running locally

```bash
pip install fastapi "pydantic>=2" sqlalchemy uvicorn httpx
uvicorn main:app --reload   # main.py should `include_router(module2.router.router)`
```

```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"agent": "OpenAI", "prompt": "Explain AI Routing"}'
```

## Suggested improvements (not yet implemented)

- Replace `InMemorySelfHealingQueue` with a durable queue (SQS/Celery) so enqueued self-healing tasks survive a process restart.
- Add a circuit breaker per agent in `executor.py` so a persistently failing provider is short-circuited instead of retried on every request.
- Emit structured metrics (latency, retry count, failure rate per agent) for the Analytics module to consume directly, rather than only via `GET /execute/{id}`.
