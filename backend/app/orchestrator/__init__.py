"""
Orchestrator — Team B2 integration layer.

Not one of the seven original modules; this is the composition root
that implements the master workflow (rule #12 in the integration
spec) by calling into Payment, Self-Healing (which itself wraps
Execution + AI Integrations), History, Reputation, and Analytics —
without modifying any of their internals.
"""

from .router import router as orchestrator_router

__all__ = ["orchestrator_router"]

