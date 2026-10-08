from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.db import get_db
from app.models.transactions import CleanTransaction
from app.schemas.analytics import AnalyticsSummary

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

def source_id_filter(stmt, source_id):
    if source_id is not None:
        stmt = stmt.where(CleanTransaction.source_id == source_id)     
    return stmt

@router.get("/summary", response_model=AnalyticsSummary)
async def analytics_summary(source_id: int | None = None, db:AsyncSession = Depends(get_db)):
    stmt = select(func.count()).select_from(CleanTransaction)
    stmt = source_id_filter(stmt, source_id)
    total = (await db.execute(stmt)).scalar_one()
    
    stmt = select(CleanTransaction.currency, func.sum(CleanTransaction.amount)).group_by(CleanTransaction.currency)
    stmt = source_id_filter(stmt, source_id)
    rows = (await db.execute(stmt)).all()
    volume_by_currency = dict(rows)

    return AnalyticsSummary(
        total_transactions=total,
        total_volume_by_currency=volume_by_currency,
        data_quality_score=0.0
    )