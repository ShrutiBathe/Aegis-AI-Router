"""
app/core/deps.py

`payments/router.py` already does

    from app.core.deps import get_current_user

No Auth module was part of this integration task/handoff, so this is a
deliberately minimal placeholder: it trusts an `X-User-Id` header
(must be a valid UUID) instead of validating a real session/JWT.

REPLACE THIS with the real Auth module's dependency (JWT/session
validation) as soon as that module exists — every route currently
importing `get_current_user` will pick it up with zero other changes,
since they only depend on the returned object having a `.id` (UUID).
"""
import uuid

from fastapi import Header, HTTPException, status


class _CurrentUser:
    """Duck-types the shape payments/router.py needs: an object with `.id`."""

    def __init__(self, user_id: uuid.UUID):
        self.id = user_id


def get_current_user(x_user_id: str | None = Header(default=None)) -> _CurrentUser:
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Id header (placeholder auth — replace with real Auth module)",
        )
    try:
        return _CurrentUser(uuid.UUID(x_user_id))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-Id header must be a valid UUID",
        )
