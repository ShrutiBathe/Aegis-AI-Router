import uuid
from decimal import Decimal

from app.database.session import engine, SessionLocal
from app.database.base import Base
from app.database import stub_models
from app.database.stub_models import User, Agent, Task

from app.payments.models import Wallet, Payment, PaymentStatus
from app.payments.service import (
    PaymentService, InsufficientBalanceError, DuplicatePaymentError,
)
from app.payments.gateway import MockGateway

Base.metadata.create_all(engine)
db = SessionLocal()

user_id = uuid.uuid4()
agent_id = uuid.uuid4()
task_id = uuid.uuid4()
db.add_all([
    User(id=user_id, email="shruti@test.com"),
    Agent(id=agent_id, name="Resume AI"),
    Task(id=task_id, prompt="Build a portfolio"),
])
db.commit()

service = PaymentService(db=db, gateway=MockGateway())

# 1. Cost estimation
est = service.estimate_cost(agent_id=agent_id, estimated_tokens=2000)
print("Estimate:", est)
assert est["estimated_cost"] == Decimal("3.00")  # 2.00 base + 1.00 token cost

# 2. Insufficient balance should raise before any wallet has funds
try:
    service.authorize_payment(user_id, agent_id, Decimal("5.00"), idempotency_key="key-1")
    raise SystemExit("expected InsufficientBalanceError")
except InsufficientBalanceError:
    print("OK: correctly rejected payment with zero balance")

# 3. Top up and retry
wallet = service.add_funds(user_id, Decimal("20.00"))
print("Balance after top-up:", wallet.balance)
assert wallet.balance == Decimal("20.00")

payment = service.authorize_payment(
    user_id, agent_id, Decimal("5.00"), idempotency_key="key-1", task_id=task_id
)
print("Authorized payment:", payment.id, payment.status, "tx:", payment.transaction_id)
assert payment.status == PaymentStatus.AUTHORIZED

wallet = service.get_balance(user_id)
print("Balance after hold:", wallet.balance)
assert wallet.balance == Decimal("15.00")

# 4. Duplicate idempotency key should be rejected
try:
    service.authorize_payment(user_id, agent_id, Decimal("5.00"), idempotency_key="key-1")
    raise SystemExit("expected DuplicatePaymentError")
except DuplicatePaymentError:
    print("OK: duplicate idempotency key correctly rejected")

# 5. Capture on success
captured = service.capture_payment(payment.id)
print("Captured:", captured.status)
assert captured.status == PaymentStatus.CAPTURED

# 6. Second task authorized, then execution fails -> self-healing triggers refund
payment2 = service.authorize_payment(
    user_id, agent_id, Decimal("4.00"), idempotency_key="key-2", task_id=task_id
)
wallet = service.get_balance(user_id)
print("Balance after second hold:", wallet.balance)
assert wallet.balance == Decimal("11.00")

refunded = service.refund_payment(payment2.id, reason="All agents failed after 3 retries")
print("Refunded:", refunded.status, refunded.failure_reason)
assert refunded.status == PaymentStatus.REFUNDED

wallet = service.get_balance(user_id)
print("Balance after refund:", wallet.balance)
assert wallet.balance == Decimal("15.00")

# 7. History
history = service.get_history(user_id)
print(f"History entries: {len(history)}")
assert len(history) == 2

print("\nALL CHECKS PASSED")
