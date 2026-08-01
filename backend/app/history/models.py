import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class ExecutionStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILURE = "failure"


class History(Base):
    """
    One row per executed request. Written by the orchestrator
    (app/orchestrator/service.py) after every task attempt, success or
    failure — per the integration spec, this table is the single source
    of truth Analytics reads from.
    """

    __tablename__ = "history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # If a `users` table exists elsewhere in the platform, point this at it.
    # Left as a plain indexed string otherwise so the module stays standalone.
    user_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)

    provider: Mapped[str] = mapped_column(String(64), index=True, nullable=False)

    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=True)

    cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # NOTE (integration): the orchestrator populates this with self_healing's
    # TaskResult.total_duration_ms — i.e. milliseconds, not seconds as the
    # original comment here said. Nothing in this codebase parses the unit
    # (schemas/service just pass the float through), so this is a doc-only
    # correction, not a behavior change.
    time_taken: Mapped[float] = mapped_column(Float, nullable=True)  # milliseconds

    # --- Added for integration ------------------------------------------
    status: Mapped[ExecutionStatus] = mapped_column(
        Enum(ExecutionStatus, name="execution_status"),
        nullable=False,
        default=ExecutionStatus.SUCCESS,
        index=True,
    )
    request_id: Mapped[str] = mapped_column(String(64), nullable=True, index=True)
    retries: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    payment_id: Mapped[str] = mapped_column(String(64), nullable=True, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    __table_args__ = (
        Index("ix_history_user_created", "user_id", "created_at"),
    )
