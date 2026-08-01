import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db
from .schemas import HistoryDeleteResponse, HistoryListResponse, HistoryResponse
from .service import HistoryService

router = APIRouter(prefix="/history", tags=["History"])


@router.get("", response_model=HistoryListResponse)
async def get_history(
    user_id: str | None = Query(default=None, description="Filter by user ID"),
    provider: str | None = Query(default=None, description="Filter by provider name"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> HistoryListResponse:
    """List execution history, newest first. Supports filtering + pagination."""
    items, total = await HistoryService.list(
        db, user_id=user_id, provider=provider, limit=limit, offset=offset
    )
    return HistoryListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[HistoryResponse.model_validate(item) for item in items],
    )


@router.get("/{history_id}", response_model=HistoryResponse)
async def get_history_item(
    history_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> HistoryResponse:
    record = await HistoryService.get_by_id(db, history_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History record not found")
    return HistoryResponse.model_validate(record)


@router.delete("/{history_id}", response_model=HistoryDeleteResponse)
async def delete_history_item(
    history_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> HistoryDeleteResponse:
    deleted = await HistoryService.delete(db, history_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History record not found")
    return HistoryDeleteResponse(id=history_id, deleted=True)
