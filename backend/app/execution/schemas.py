"""
schemas.py — Module 2 (Execution Engine)

Pydantic contracts for the public API. Keeping these separate from
models.py means the DB schema can evolve without breaking the wire format,
and vice versa.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .models import ExecutionStatus


class ExecuteRequest(BaseModel):
    """Body for POST /execute."""

    agent: str = Field(..., min_length=1, description="Selected AI agent, e.g. 'OpenAI'")
    prompt: str = Field(..., min_length=1, max_length=8000, description="Prompt to send to the agent")
    params: Optional[dict[str, Any]] = Field(
        default=None, description="Optional agent-specific parameters (temperature, max_tokens, ...)"
    )
    request_id: Optional[str] = Field(
        default=None, description="Optional client-supplied idempotency key (UUID recommended)"
    )

    @field_validator("agent")
    @classmethod
    def _normalize_agent(cls, v: str) -> str:
        return v.strip()

    @field_validator("prompt")
    @classmethod
    def _strip_prompt(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("prompt must not be empty or whitespace-only")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"agent": "OpenAI", "prompt": "Explain AI Routing"}
        }
    )


class ExecuteResponse(BaseModel):
    """Response for POST /execute."""

    id: str
    agent: str
    status: ExecutionStatus
    response: Optional[str] = None
    error: Optional[str] = None
    latency_ms: Optional[float] = None
    retries: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExecutionRecordOut(ExecuteResponse):
    """Response for GET /execute/{id} — includes the update timestamp."""

    updated_at: datetime
