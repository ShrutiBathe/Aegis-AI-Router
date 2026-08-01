"""
Payment module — service layer.

All money-moving logic lives here so the router stays thin and the gateway
stays swappable. Uses SELECT ... FOR UPDATE on the wallet row to avoid a
race condition where two concurrent task submissions could both read the
same balance and both pass an affordability check.
"""
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .models import Wallet, Payment, PaymentStatus
from .gateway import PaymentGateway, GatewayResult


class InsufficientBalanceError(Exception):
    pass


class DuplicatePaymentError(Exception):
    """Raised when an idempotency_key has already been used."""
    pass


class PaymentNotFoundError(Exception):
    pass


class InvalidPaymentStateError(Exception):
    pass


# Flat per-request base rate; extend with a real pricing table keyed by
# agent + task complexity once the marketplace module has real agent pricing.
DEFAULT_BASE_RATE = Decimal("2.00")
PER_1K_TOKENS_RATE = Decimal("0.50")


class PaymentService:
    def __init__(self, db: Session, gateway: PaymentGateway):
        self.db = db
        self.gateway = gateway

    # ---------- Wallet ----------

    def get_or_create_wallet(self, user_id: UUID) -> Wallet:
        wallet = self.db.query(Wallet).filter(Wallet.user_id == user_id).first()
        if wallet is None:
            wallet = Wallet(user_id=user_id, balance=Decimal("0"))
            self.db.add(wallet)
            self.db.commit()
            self.db.refresh(wallet)
        return wallet

    def get_balance(self, user_id: UUID) -> Wallet:
        return self.get_or_create_wallet(user_id)

    def add_funds(self, user_id: UUID, amount: Decimal, external_reference: Optional[str] = None) -> Wallet:
        wallet = (
            self.db.query(Wallet)
            .filter(Wallet.user_id == user_id)
            .with_for_update()
            .first()
        )
        if wallet is None:
            wallet = Wallet(user_id=user_id, balance=Decimal("0"))
            self.db.add(wallet)
            self.db.flush()

        wallet.balance += amount
        self.db.commit()
        self.db.refresh(wallet)
        return wallet

    # ---------- Cost estimation ----------

    def estimate_cost(self, agent_id: UUID, estimated_tokens: Optional[int] = None) -> dict:
        # TODO: replace DEFAULT_BASE_RATE with a lookup against the agent's
        # own price field once the marketplace/agents table exists.
        base = DEFAULT_BASE_RATE
        token_cost = Decimal("0")
        if estimated_tokens:
            token_cost = (Decimal(estimated_tokens) / Decimal(1000)) * PER_1K_TOKENS_RATE

        total = base + token_cost
        return {
            "agent_id": agent_id,
            "estimated_cost": total,
            "currency": "INR",
            "breakdown": {
                "base_rate": str(base),
                "token_cost": str(token_cost),
            },
        }

    # ---------- Authorize / Capture / Refund ----------

    def authorize_payment(
        self,
        user_id: UUID,
        agent_id: UUID,
        amount: Decimal,
        idempotency_key: str,
        currency: str = "INR",
        task_id: Optional[UUID] = None,
    ) -> Payment:
        """Hold funds for a task. Does not finalize the charge — call
        capture_payment() once execution succeeds, or refund_payment() /
        mark_failed() if it doesn't."""

        existing = self.db.query(Payment).filter(Payment.idempotency_key == idempotency_key).first()
        if existing is not None:
            raise DuplicatePaymentError(f"Payment already exists for idempotency_key={idempotency_key}")

        wallet = (
            self.db.query(Wallet)
            .filter(Wallet.user_id == user_id)
            .with_for_update()
            .first()
        )
        if wallet is None or wallet.balance < amount:
            raise InsufficientBalanceError("Wallet balance too low for this task")

        result: GatewayResult = self.gateway.authorize(amount, currency, reference=idempotency_key)
        if not result.success:
            raise InsufficientBalanceError(result.error or "Gateway declined authorization")

        # Hold the funds by debiting immediately; a refund puts them back
        # if execution ultimately fails. Simpler than a separate "held"
        # ledger column for a hackathon-scale build.
        wallet.balance -= amount

        payment = Payment(
            wallet_id=wallet.id,
            user_id=user_id,
            task_id=task_id,
            agent_id=agent_id,
            amount=amount,
            currency=currency,
            status=PaymentStatus.AUTHORIZED,
            idempotency_key=idempotency_key,
            transaction_id=result.transaction_id,
        )
        self.db.add(payment)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise DuplicatePaymentError(f"Payment already exists for idempotency_key={idempotency_key}")

        self.db.refresh(payment)
        return payment

    def capture_payment(self, payment_id: UUID) -> Payment:
        """Call this once the execution engine reports success."""
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if payment is None:
            raise PaymentNotFoundError(str(payment_id))
        if payment.status != PaymentStatus.AUTHORIZED:
            raise InvalidPaymentStateError(f"Cannot capture payment in status {payment.status}")

        result = self.gateway.capture(payment.transaction_id)
        if not result.success:
            raise InvalidPaymentStateError(result.error or "Gateway capture failed")

        payment.status = PaymentStatus.CAPTURED
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def refund_payment(self, payment_id: UUID, reason: str) -> Payment:
        """Call this from the self-healing path once every agent retry has
        been exhausted and the task ultimately fails."""
        from sqlalchemy.sql import func as sqlfunc

        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if payment is None:
            raise PaymentNotFoundError(str(payment_id))
        if payment.status not in (PaymentStatus.AUTHORIZED, PaymentStatus.CAPTURED):
            raise InvalidPaymentStateError(f"Cannot refund payment in status {payment.status}")

        result = self.gateway.refund(payment.transaction_id, payment.amount)
        if not result.success:
            raise InvalidPaymentStateError(result.error or "Gateway refund failed")

        wallet = self.db.query(Wallet).filter(Wallet.id == payment.wallet_id).with_for_update().first()
        wallet.balance += payment.amount

        payment.status = PaymentStatus.REFUNDED
        payment.failure_reason = reason
        payment.refunded_at = sqlfunc.now()
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def mark_failed(self, payment_id: UUID, reason: str) -> Payment:
        """Use when a payment authorization itself fails (before any hold
        succeeded) — no refund needed since no funds moved."""
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if payment is None:
            raise PaymentNotFoundError(str(payment_id))
        payment.status = PaymentStatus.FAILED
        payment.failure_reason = reason
        self.db.commit()
        self.db.refresh(payment)
        return payment

    # ---------- History ----------

    def get_history(
        self,
        user_id: UUID,
        status: Optional[PaymentStatus] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Payment]:
        query = self.db.query(Payment).filter(Payment.user_id == user_id)
        if status:
            query = query.filter(Payment.status == status)
        return (
            query.order_by(Payment.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
