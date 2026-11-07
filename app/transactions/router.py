from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.api.deps import Pagination, pagination_params
from app.api.filters import source_id_filter, transaction_filters
from app.auth.deps import get_current_user, resolve_source_id
from app.db import get_db
from app.models.transactions import CleanTransaction
from app.models.users import User
from app.schemas.transactions import TransactionListResponse


router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])

@router.get("", response_model=TransactionListResponse)
async def list_transactions(
    source_id: int | None = None,
    currency: str | None = None,
    status: str | None = None,
    quality_flag: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: Pagination = Depends(pagination_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    approved_source_id = resolve_source_id(current_user, source_id)

    stmt = select(func.count()).select_from(CleanTransaction)
    stmt = source_id_filter(stmt, approved_source_id)
    stmt = transaction_filters(stmt, currency, status, quality_flag, date_from, date_to)
    total = (await db.execute(stmt)).scalar_one()

    stmt = select(CleanTransaction)
    stmt = source_id_filter(stmt, approved_source_id).order_by(CleanTransaction.transaction_date.desc(),
                                             CleanTransaction.id.desc()).limit(page.limit).offset(page.offset)
    stmt = transaction_filters(stmt, currency, status, quality_flag, date_from, date_to)
    items = (await db.execute(stmt)).scalars().all()

    return TransactionListResponse(
        items = items,
        total = total,
        limit = page.limit,
        offset = page.offset
    )

    