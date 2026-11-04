from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.api.filters import source_id_filter
from app.db import get_db
from app.models.transactions import CleanTransaction
from app.models.users import User
from app.schemas.analytics import AnalyticsSummary
from app.models.quality import DataQualityIssue
from app.models.transactions import RawTransaction
from app.auth.deps import resolve_source_id, get_current_user

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

@router.get("/summary", response_model=AnalyticsSummary)
async def analytics_summary(current_user: User = Depends(get_current_user), source_id: int | None = None, db:AsyncSession = Depends(get_db)):
    approved_source_id = resolve_source_id(current_user, source_id)
    stmt = select(func.count()).select_from(CleanTransaction)
    stmt = source_id_filter(stmt, approved_source_id)
    total = (await db.execute(stmt)).scalar_one()
    
    stmt = select(CleanTransaction.currency, func.sum(CleanTransaction.amount)).group_by(CleanTransaction.currency)
    stmt = source_id_filter(stmt, approved_source_id)
    rows = (await db.execute(stmt)).all()
    volume_by_currency = dict(rows)

    stmt = select(func.count(func.distinct(DataQualityIssue.raw_id))).where(DataQualityIssue.issue_type.in_(["invalid_amount", "invalid_currency", "invalid_timestamp"]))
    if approved_source_id is not None:
        stmt = stmt.join(RawTransaction, DataQualityIssue.raw_id == RawTransaction.id).where(RawTransaction.source_id == approved_source_id)
    error = (await db.execute(stmt)).scalar_one()

    if total == 0 and error == 0:
        result = 0.0
    else:
        result = round(total / (total + error) * 100, 2)


    return AnalyticsSummary(
        total_transactions=total,
        total_volume_by_currency=volume_by_currency,
        data_quality_score=result
    )