# Self-Healing Module

Part of **Team B2 — Service Execution & Marketplace Operations**.

## Purpose

Automatically recover when an AI provider fails, without the caller (Execution
module) needing to know or care which provider ultimately served the request.

```
OpenAI
   ↓
Timeout
   ↓
Retry (backoff)
   ↓
Still fails (retries exhausted)
   ↓
Circuit breaker opens for OpenAI
   ↓
Switch to Gemini (failover)
   ↓
Success
```

## Strategies

| Strategy | File | What it does |
|---|---|---|
| Retry | `retry.py` | Exponential backoff with jitter, per-attempt timeout, bounded attempt count |
| Circuit Breaker | `circuit_breaker.py` | Per-provider CLOSED → OPEN → HALF_OPEN state machine; stops hammering a dead provider |
| Provider Switching | `failover.py` | Tries providers in order (optionally ranked by reputation score) until one succeeds |
| Orchestration | `service.py` | Wires retry + circuit breaker + failover into one call, emits events for History/Analytics |
| API | `router.py` | FastAPI endpoints the rest of the platform (or ops tooling) calls |

## File layout

```
self_healing/
├── __init__.py           # public exports
├── provider_interface.py # adapter contract for the AI Integrations module
├── retry.py
├── circuit_breaker.py
├── failover.py
├── service.py
├── router.py
└── README.md
```

## How it fits together

```
Execution module
      │
      ▼
POST /self-healing/execute  (router.py)
      │
      ▼
SelfHealingService.execute_task()   (service.py)
      │
      ▼
FailoverExecutor.execute(candidates) (failover.py)
      │   for each candidate provider, in order:
      ▼
CircuitBreaker.call(...)            (circuit_breaker.py)
      │   if CLOSED/HALF_OPEN, proceed; if OPEN, skip to next provider
      ▼
Retry.run(...)                      (retry.py)
      │   exponential backoff across attempts
      ▼
provider_registry.get_client(name).execute(prompt)   (AI Integrations module)
```

## Integration with the AI Integrations module

`provider_interface.py` defines the contract this module expects from a
provider client:

```python
class AIProviderClient(Protocol):
    provider_name: str
    async def execute(self, prompt: str, **kwargs) -> AIProviderResponse: ...
```

and from the registry:

```python
class AIProviderRegistry(Protocol):
    def get_client(self, provider_name: str) -> AIProviderClient: ...
    def list_providers(self) -> list[str]: ...
```

By default it imports `provider_registry` from `ai_integrations.registry`.
**Update `AI_INTEGRATIONS_IMPORT_PATH` in `provider_interface.py`** to match
the real module's package path once merged. Until then, or in unit tests, a
built-in in-memory stub registry (openai/gemini/claude/groq/ollama, 0%
failure rate by default) is used automatically so this module runs
standalone.

Provider-side failures should raise `AIProviderError(provider, message,
retryable=True/False)` from the AI Integrations module so retry/failover know
whether to keep trying or give up immediately (e.g. bad API key → not
retryable; rate limit/timeout → retryable).

## Reputation-aware failover (optional)

`SelfHealingService` accepts a `reputation_scorer: Callable[[str], float]`.
Wire this to the Reputation module's trust-score lookup so the failover
chain tries the highest-trust healthy provider first instead of a fixed
order:

```python
from reputation.scoring import get_trust_score  # Reputation module

service = SelfHealingService(reputation_scorer=get_trust_score)
```

## Events for History / Analytics

`SelfHealingService(on_event=callback)` fires a callback with a plain dict
for `task_started`, `task_succeeded`, and `task_failed` events (provider
attempted, winning provider, duration, errors). Wire the History module's
writer and the Analytics module's aggregator to this hook — this module has
no direct dependency on either, so ordering/rollout of those modules doesn't
block this one.

```python
def on_event(event: dict):
    history.record(event)
    analytics.ingest(event)

service = SelfHealingService(on_event=on_event)
```

## API

Mount in the main app:

```python
from self_healing.router import router as self_healing_router
app.include_router(self_healing_router)
```

| Method | Path | Description |
|---|---|---|
| POST | `/self-healing/execute` | Run a task with full retry/circuit-breaker/failover protection |
| GET | `/self-healing/circuit-breakers` | Current state of every provider's breaker |
| POST | `/self-healing/circuit-breakers/reset` | Force a breaker (or all) back to CLOSED — ops/admin use |
| GET | `/self-healing/health` | Liveness check |

### Example request

```bash
curl -X POST http://localhost:8000/self-healing/execute \
  -H "Content-Type: application/json" \
  -d '{
        "prompt": "Summarize this contract clause",
        "preferred_providers": ["openai", "gemini", "claude"]
      }'
```

### Example response

```json
{
  "request_id": "3f1c9e2a-...",
  "success": true,
  "winning_provider": "gemini",
  "attempted_providers": ["openai", "gemini"],
  "total_duration_ms": 842.3,
  "response": {
    "provider": "gemini",
    "content": "...",
    "latency_ms": 210.4,
    "metadata": {}
  },
  "error": null
}
```

## Configuration

Defaults are set in `RetryConfig` and `CircuitBreakerConfig`; override by
constructing `SelfHealingService(retry_config=..., circuit_breaker_config=...)`.

| Setting | Default | Meaning |
|---|---|---|
| `max_attempts` | 3 | Retry attempts per provider before failing over |
| `base_delay_seconds` | 0.5 | First backoff delay |
| `backoff_multiplier` | 2.0 | Delay growth per attempt |
| `max_delay_seconds` | 8.0 | Backoff ceiling |
| `timeout_seconds` | 10.0 | Per-attempt timeout |
| `failure_threshold` | 5 | Consecutive failures before a breaker opens |
| `recovery_timeout_seconds` | 30.0 | How long a breaker stays OPEN before trying HALF_OPEN |
| `success_threshold` | 2 | Consecutive successes in HALF_OPEN needed to close |

## Testing without the real AI Integrations module

The bundled stub registry lets you exercise every code path (success, retry,
timeout, circuit open, failover) with no external API calls:

```python
import asyncio
from self_healing.service import SelfHealingService, TaskRequest
from self_healing import provider_interface as pi

# force openai to always fail so failover kicks in
pi.provider_registry._clients["openai"].failure_rate = 1.0

service = SelfHealingService()
result = asyncio.run(service.execute_task(
    TaskRequest(prompt="test", preferred_providers=["openai", "gemini"])
))
print(result.success, result.winning_provider)  # True gemini
```

## Notes / follow-ups for integration

- Swap the stub import in `provider_interface.py` for the real
  `ai_integrations.registry.provider_registry` once that module exposes the
  path (single-line change, contract already matches).
- Wire `on_event` in `service.py` to the History and Analytics modules.
- Wire `reputation_scorer` to the Reputation module once its trust-score API
  is finalized.
- Circuit breaker state is currently in-process/in-memory; if B2 runs as
  multiple replicas behind a load balancer, consider backing
  `CircuitBreakerRegistry` with shared state (e.g. Redis) so all replicas
  agree on a provider's health.
