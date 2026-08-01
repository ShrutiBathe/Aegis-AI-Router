"""
app/database/base.py

Shared SQLAlchemy declarative Base for modules built on the *sync*
ORM (currently: Payment). `payments/models.py` already does

    from app.database.base import Base

so this file just has to exist and export `Base`. Execution keeps its
own separate `Base` in `execution/models.py` (untouched, per the
integration rules) — that's fine, two declarative registries can
target the same physical database without conflict as long as table
names don't collide, and they don't (wallets/payments vs
execution_records).
"""
from sqlalchemy.orm import declarative_base

Base = declarative_base()
