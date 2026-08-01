"""
models.py — Module 2 (Execution Engine)

SQLAlchemy ORM model that persists every /execute call: which agent was
asked, what the prompt was, what came back (or what went wrong), and how
long it took. This is the single source of truth Analytics, History, and
Reputation (Module 1's fan-out) read from.
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum as SAEnum, Float, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ExecutionStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    HEALING = "healing"  # set by the Self-Healing module while it retries/repairs


def _new_id() -> str:
    return str(uuid.uuid4())


class ExecutionRecord(Base):
    """One row per /execute request/response cycle."""

    __tablename__ = "execution_records"

    id = Column(String(36), primary_key=True, default=_new_id)
    agent = Column(String(64), nullable=False, index=True)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    status = Column(SAEnum(ExecutionStatus), nullable=False, default=ExecutionStatus.PENDING, index=True)
    error = Column(Text, nullable=True)
    latency_ms = Column(Float, nullable=True)
    retries = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return f"<ExecutionRecord id={self.id} agent={self.agent} status={self.status}>"
