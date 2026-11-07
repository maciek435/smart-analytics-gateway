from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy import func, literal_column, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.filters import source_id_filter, transaction_filters
from app.auth.deps import get_current_user, resolve_source_id
from app.db import get_db
from app.etl.constants import BLOCKING_ISSUE_TYPES
from app.models.quality import DataQualityIssue
from app.models.transactions import CleanTransaction, RawTransaction
from app.models.users import User
from app.schemas.analytics import AnalyticsSummary, TimeseriesResponse

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


def rejected_filters(stmt, source_id, date_from, date_to):
    """Filtry dla odrzuconych: źródło i data PRZYJĘCIA rekordu (received_at)."""
    stmt = stmt.where(DataQualityIssue.issue_type.in_(BLOCKING_ISSUE_TYPES))
    if source_id is not None:
        stmt = stmt.where(RawTransaction.source_id == source_id)
    if date_from is not None:
        stmt = stmt.where(RawTransaction.received_at >= date_from)
    if date_to is not None:
        stmt = stmt.where(RawTransaction.received_at <= date_to)
    return stmt


@router.get("/summary", response_model=AnalyticsSummary)
async def analytics_summary(
    source_id: int | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    approved_source_id = resolve_source_id(current_user, source_id)

    stmt = select(func.count()).select_from(CleanTransaction)
    stmt = source_id_filter(stmt, approved_source_id)
    stmt = transaction_filters(stmt, date_from=date_from, date_to=date_to)
    total = (await db.execute(stmt)).scalar_one()

    stmt = select(CleanTransaction.currency, func.sum(CleanTransaction.amount)).group_by(
        CleanTransaction.currency
    )
    stmt = source_id_filter(stmt, approved_source_id)
    stmt = transaction_filters(stmt, date_from=date_from, date_to=date_to)
    volume_by_currency = dict((await db.execute(stmt)).all())

    stmt = (
        select(func.count(func.distinct(DataQualityIssue.raw_id)))
        .select_from(DataQualityIssue)
        .join(RawTransaction, DataQualityIssue.raw_id == RawTransaction.id)
    )
    stmt = rejected_filters(stmt, approved_source_id, date_from, date_to)
    error = (await db.execute(stmt)).scalar_one()

    score = 0.0 if total == 0 and error == 0 else round(total / (total + error) * 100, 2)

    return AnalyticsSummary(
        total_transactions=total,
        total_volume_by_currency=volume_by_currency,
        data_quality_score=score,
    )


@router.get("/timeseries", response_model=TimeseriesResponse)
async def analytics_timeseries(
    group_by: Literal["day", "week", "month"] = "day",
    source_id: int | None = None,
    currency: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    approved_source_id = resolve_source_id(current_user, source_id)

    # Jednostka wstawiona jako literał SQL (nie parametr): Postgres wymaga, żeby
    # wyrażenie w SELECT i GROUP BY było identyczne. Literal[...] gwarantuje,
    # że to tylko "day" / "week" / "month", więc nie ma ryzyka SQL injection.
    unit = literal_column(f"'{group_by}'")

    period = func.date_trunc(unit, CleanTransaction.transaction_date).label("period")
    stmt = (
        select(
            period,
            CleanTransaction.currency,
            func.count().label("transactions"),
            func.sum(CleanTransaction.amount).label("volume"),
        )
        .group_by(period, CleanTransaction.currency)
        .order_by(period, CleanTransaction.currency)
    )
    stmt = source_id_filter(stmt, approved_source_id)
    stmt = transaction_filters(stmt, currency=currency, date_from=date_from, date_to=date_to)
    points = (await db.execute(stmt)).all()

    rperiod = func.date_trunc(unit, RawTransaction.received_at).label("period")
    rstmt = (
        select(rperiod, func.count(func.distinct(DataQualityIssue.raw_id)).label("rejected"))
        .select_from(DataQualityIssue)
        .join(RawTransaction, DataQualityIssue.raw_id == RawTransaction.id)
        .group_by(rperiod)
        .order_by(rperiod)
    )
    rstmt = rejected_filters(rstmt, approved_source_id, date_from, date_to)
    rejected = (await db.execute(rstmt)).all()

    return TimeseriesResponse(
        group_by=group_by,
        points=[
            {"period": r.period, "currency": r.currency,
             "transactions": r.transactions, "volume": float(r.volume)}
            for r in points
        ],
        rejected=[{"period": r.period, "rejected": r.rejected} for r in rejected],
    )