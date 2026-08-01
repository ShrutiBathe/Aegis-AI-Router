"""
Analytics Module — Team B2 (Service Execution & Marketplace Operations)

Aggregates platform statistics (dashboard cards + charts) from the
History module's execution log. Owns no tables of its own — it is a
read-only aggregation layer over `history` (and, per open items in the
README, ideally over the Payment module's transactions table for
revenue and a real Users table for signups).
"""

from .router import router as analytics_router

__all__ = ["analytics_router"]
