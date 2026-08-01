"""
History Module — Team B2 (Service Execution & Marketplace Operations)

Stores every execution: user requests, provider used, prompt/response,
cost, and timing. Exposes read + delete endpoints for the history log.
"""

from .router import router as history_router

__all__ = ["history_router"]
