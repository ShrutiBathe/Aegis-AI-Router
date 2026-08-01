"""
Payment module — database models.

Adjust the import on the next line to match wherever your project's
declarative Base and User model actually live (e.g. `app.database.base`).
"""
import enum
import uuid

from sqlalchemy import (
    Column, String, Numeric, DateTime, ForeignKey, Enum, Text, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base  # <-- adjust to your project structure


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"       # created, not yet sent to chain
    AUTHORIZED = "authorized" # funds held, task not yet complete
    CAPTURED = "captured"     # task succeeded, funds actually moved
    FAILED = "failed"         # execution or payment failed outright
    REFUNDED = "refunded"     # authorized/captured funds returned to user


class Wallet(Base):
    """One wallet per user. Balance is the single source of truth for
    'can this user afford to submit a task' checks."""
    __tablename__ = "wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False, index=True)

    # Numeric, never Float — avoids floating point drift on money.
    balance = Column(Numeric(14, 4), nullable=False, default=0)
    currency = Column(String(10), nullable=False, default="INR")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    payments = relationship("Payment", back_populates="wallet")


class Payment(Base):
    """A single payment record, tied to a task + agent.

    Lifecycle: PENDING -> AUTHORIZED -> CAPTURED
                                  \\-> FAILED -> REFUNDED (if it was authorized/captured)
    """
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False, index=True)

    amount = Column(Numeric(14, 4), nullable=False)
    currency = Column(String(10), nullable=False, default="INR")
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING, index=True)

    # Prevents double-charging if a client retries a request after a timeout.
    idempotency_key = Column(String(64), unique=True, nullable=False, index=True)

    # On-chain / gateway reference (Algorand tx id, x402 payment id, etc.)
    transaction_id = Column(String(128), nullable=True, index=True)

    failure_reason = Column(Text, nullable=True)
    refunded_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    wallet = relationship("Wallet", back_populates="payments")

    __table_args__ = (
        Index("ix_payments_user_created", "user_id", "created_at"),
    )
