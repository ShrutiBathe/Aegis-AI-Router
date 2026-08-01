# Module 1 — Payment

Authorize/capture/refund payment module for Aegis Router, built on the
"hold funds → capture on success, refund on exhausted retries" pattern
instead of "charge then refund on failure."

## Files

- `models.py` — `Wallet` and `Payment` SQLAlchemy models
- `schemas.py` — Pydantic request/response schemas
- `gateway.py` — `PaymentGateway` interface + `MockGateway` (works now) +
  `AlgorandGateway` (stub — wire up `algosdk` + your x402 client here)
- `service.py` — `PaymentService`: all wallet/payment business logic
- `router.py` — FastAPI routes

## Wiring into your project

1. Copy this folder into `backend/app/payments/`.
2. Fix the two adjusted imports:
   - `models.py`: `from app.database.base import Base`
   - `router.py`: `get_db` and `get_current_user`
3. Register the routers in your `main.py`:
   ```python
   from app.payments.router import router as payment_router, wallet_router
   app.include_router(payment_router)
   app.include_router(wallet_router)
   ```
4. Run a migration (Alembic) to create `wallets` and `payments` tables.

## How other modules should call this

- **Task Submission** → `GET /payment/estimate` before showing the user a cost.
- **Router/Execution Engine** → `POST /payment/pay` right after an agent is
  selected (this holds the funds), then `POST /payment/capture` once the
  agent returns a successful result.
- **Self-Healing** → only calls `POST /payment/refund` after it has
  exhausted retries across every candidate agent — not on the first
  failure. This avoids a refund-then-recharge round trip per retry.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/wallet/balance` | Current wallet balance |
| POST | `/wallet/add` | Top up wallet |
| GET | `/payment/estimate` | Estimate cost before submitting a task |
| POST | `/payment/pay` | Authorize (hold) funds for a task |
| POST | `/payment/capture` | Settle a held payment after execution succeeds |
| POST | `/payment/refund` | Return held/captured funds after execution ultimately fails |
| GET | `/payment/history` | Paginated payment history for the current user |

## Verified

`test_payment_flow.py` (run against an in-memory SQLite DB) exercises:
zero-balance rejection → top-up → authorize/hold → duplicate idempotency-key
rejection → capture → second authorize → refund → history. All assertions
pass.
