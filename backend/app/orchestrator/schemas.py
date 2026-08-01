"""
app/orchestrator/schemas.py

Request/response contracts for the master workflow endpoint. New file —
none of the seven existing modules had a schema that represents "one
end-to-end task run" (Payment/Execution/History/Reputation/Analytics
each only model their own slice).
"""
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TaskRunRequest(BaseModel):
    user_id: UUID
    prompt: str = Field(..., min_length=1, max_length=8000)
    preferred_providers: Optional[list[str]] = Field(
        default=None,
        description="Ordered candidate provider chain, e.g. ['claude','groq','ollama']. "
                    "Defaults to self_healing's standard fallback chain.",
    )
    extra_params: dict[str, Any] = Field(default_factory=dict)
    estimated_tokens: Optional[int] = Field(
        default=None, description="Optional signal for Payment's cost estimate"
    )
    idempotency_key: Optional[str] = Field(
        default=None, description="Optional client-supplied idempotency key; generated if omitted"
    )


class PaymentSummary(BaseModel):
    id: UUID
    status: str
    amount: Decimal
    currency: str


class TaskRunResponse(BaseModel):
    request_id: str
    success: bool
    provider: Optional[str]
    response: Optional[str]
    error: Optional[str]
    attempted_providers: list[str]
    retries: int
    latency_ms: float
    payment: Optional[PaymentSummary]
    history_id: Optional[UUID]
