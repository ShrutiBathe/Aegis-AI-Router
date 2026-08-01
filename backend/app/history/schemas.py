import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .models import ExecutionStatus


class HistoryCreate(BaseModel):
    """Used internally by the orchestrator to log a completed task attempt."""

    user_id: str
    provider: str
    prompt: str
    response: str | None = None
    cost: float = 0.0
    time_taken: float | None = None  # milliseconds
    status: ExecutionStatus = ExecutionStatus.SUCCESS
    request_id: str | None = None
    retries: int = 0
    payment_id: str | None = None


class HistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: str
    provider: str
    prompt: str
    response: str | None
    cost: float
    time_taken: float | None
    status: ExecutionStatus
    request_id: str | None
    retries: int
    payment_id: str | None
    created_at: datetime


class HistoryListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[HistoryResponse]


class HistoryDeleteResponse(BaseModel):
    id: uuid.UUID
    deleted: bool = Field(default=True)
