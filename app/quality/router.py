from collections import defaultdict
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import Pagination, pagination_params
from app.auth.deps import get_current_user, resolve_source_id
from app.db import get_db
from app.etl.constants import BLOCKING_ISSUE_TYPES
from app.models.quality import DataQualityIssue
from app.models.transactions import RawTransaction
from app.models.users import User
from app.schemas.quality import (
    RejectedTransactionListResponse,
    RejectedTransactionResponse,
)

router = APIRouter(prefix="/api/v1/rejected-transactions", tags=["quality"])


@router.get("", response_model=RejectedTransactionListResponse)
async def list_rejected_transactions(
    source_id: int | None = None,
    issue_type: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: Pagination = Depends(pagination_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    approved_source_id = resolve_source_id(current_user, source_id)

    # które typy błędów uznajemy za "odrzucenie" (filtr issue_type zawęża, nie rozszerza)
    issue_types = (
        BLOCKING_ISSUE_TYPES
        if issue_type is None
        else [t for t in BLOCKING_ISSUE_TYPES if t == issue_type]
    )
    rejected_ids = select(DataQualityIssue.raw_id).where(
        DataQualityIssue.issue_type.in_(issue_types)
    )

    # jedna lista warunków używana i do licznika, i do listy
    conditions = [RawTransaction.id.in_(rejected_ids)]
    if approved_source_id is not None:
        conditions.append(RawTransaction.source_id == approved_source_id)
    if date_from is not None:
        conditions.append(RawTransaction.received_at >= date_from)
    if date_to is not None:
        conditions.append(RawTransaction.received_at <= date_to)

    total = (
        await db.execute(
            select(func.count()).select_from(RawTransaction).where(*conditions)
        )
    ).scalar_one()

    stmt = (
        select(RawTransaction)
        .where(*conditions)
        .order_by(RawTransaction.received_at.desc(), RawTransaction.id.desc())
        .limit(page.limit)
        .offset(page.offset)
    )
    rows = (await db.execute(stmt)).scalars().all()

    issues_by_raw = defaultdict(list)
    raw_ids = [row.id for row in rows]
    if raw_ids:
        issues = (
            await db.execute(
                select(DataQualityIssue)
                .where(DataQualityIssue.raw_id.in_(raw_ids))
                .order_by(DataQualityIssue.id)
            )
        ).scalars().all()
        for issue in issues:
            issues_by_raw[issue.raw_id].append(issue)

    items = [
        RejectedTransactionResponse(
            raw_id=row.id,
            source_id=row.source_id,
            payload=row.payload,
            received_at=row.received_at,
            issues=issues_by_raw[row.id],
        )
        for row in rows
    ]

    return RejectedTransactionListResponse(
        items=items, total=total, limit=page.limit, offset=page.offset
    )