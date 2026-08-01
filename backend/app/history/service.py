import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import History
from .schemas import HistoryCreate


class HistoryService:
    """Business logic for reading/writing execution history records."""

    @staticmethod
    async def create(db: AsyncSession, data: HistoryCreate) -> History:
        record = History(
            user_id=data.user_id,
            provider=data.provider,
            prompt=data.prompt,
            response=data.response,
            cost=data.cost,
            time_taken=data.time_taken,
            status=data.status,
            request_id=data.request_id,
            retries=data.retries,
            payment_id=data.payment_id,
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record

    @staticmethod
    async def list(
        db: AsyncSession,
        user_id: str | None = None,
        provider: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[History], int]:
        query = select(History)
        count_query = select(func.count()).select_from(History)

        if user_id:
            query = query.where(History.user_id == user_id)
            count_query = count_query.where(History.user_id == user_id)
        if provider:
            query = query.where(History.provider == provider)
            count_query = count_query.where(History.provider == provider)

        query = query.order_by(History.created_at.desc()).limit(limit).offset(offset)

        total = (await db.execute(count_query)).scalar_one()
        items = (await db.execute(query)).scalars().all()
        return list(items), total

    @staticmethod
    async def get_by_id(db: AsyncSession, history_id: uuid.UUID) -> History | None:
        result = await db.execute(select(History).where(History.id == history_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def delete(db: AsyncSession, history_id: uuid.UUID) -> bool:
        record = await HistoryService.get_by_id(db, history_id)
        if record is None:
            return False
        await db.delete(record)
        await db.commit()
        return True
