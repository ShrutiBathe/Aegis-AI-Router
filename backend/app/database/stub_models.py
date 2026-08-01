"""
app/database/stub_models.py

`payments/models.py` declares real foreign keys to `users.id`,
`agents.id`, and `tasks.id` — but no User/Agent/Task module was part of
this integration handoff, and Team B2 doesn't own those tables. Without
*something* named `users`/`agents`/`tasks` in the same metadata, Postgres
will reject `CREATE TABLE wallets (...)` / `CREATE TABLE payments (...)`
with an undefined-table error on the FK constraint.

These are placeholder tables ONLY — just enough columns to satisfy the
foreign keys so the Payment module's own (untouched) models/service/router
work end-to-end for local dev and integration testing. Class names
(`User`, `Agent`, `Task`) and field shapes match what payments'
pre-existing test_payment_flow.py already expects.

DELETE THIS FILE once the real Auth module (users) and Marketplace module
(agents, tasks) land, and let Payment's foreign keys point at their real
tables instead.
"""
import uuid

from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=True)


class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Matches the provider name used across Execution / Self-Healing /
    # AI Integrations (e.g. "openai", "claude", "groq"), so the
    # orchestrator can derive a stable agent_id per provider — see
    # app/orchestrator/service.py:provider_to_agent_id().
    name = Column(String(64), nullable=True, unique=True)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt = Column(Text, nullable=True)
