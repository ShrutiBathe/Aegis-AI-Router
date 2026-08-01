"""
Payment module — request/response schemas.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from .models import PaymentStatus


# ---------- Wallet ----------

class WalletBalanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    balance: Decimal
    currency: str
    updated_at: datetime


class WalletTopUpRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Amount to add to wallet")
    currency: str = Field(default="INR")
    # Reference from the on-chain top-up transaction (Algorand tx id, UPI ref, etc.)
    external_reference: Optional[str] = None


class WalletTopUpResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    balance: Decimal
    currency: str


# ---------- Cost estimation ----------

class CostEstimateRequest(BaseModel):
    agent_id: UUID
    # optional signal from the planner about how "big" the task is;
    # lets pricing scale beyond a flat per-request fee if you want that later
    estimated_tokens: Optional[int] = None


class CostEstimateResponse(BaseModel):
    agent_id: UUID
    estimated_cost: Decimal
    currency: str
    breakdown: dict


# ---------- Payment (charge) ----------

class PaymentCreateRequest(BaseModel):
    task_id: Optional[UUID] = None
    agent_id: UUID
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="INR")
    idempotency_key: str = Field(..., min_length=8, max_length=64)


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    task_id: Optional[UUID]
    agent_id: UUID
    amount: Decimal
    currency: str
    status: PaymentStatus
    transaction_id: Optional[str]
    created_at: datetime


class PaymentCaptureRequest(BaseModel):
    payment_id: UUID


class RefundRequest(BaseModel):
    payment_id: UUID
    reason: str = Field(..., max_length=255)


class PaymentHistoryQuery(BaseModel):
    status: Optional[PaymentStatus] = None
    limit: int = Field(default=20, le=100)
    offset: int = Field(default=0, ge=0)
