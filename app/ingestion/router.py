from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from sqlalchemy import select

from app.auth.deps import get_current_user, resolve_source_id
from app.db import get_db
from app.models import RawTransaction
from app.models.users import User
from app.schemas.ingestion import IngestBatchRequest, IngestResponse
from app.models import Source

router = APIRouter(prefix="/api/v1/ingest", tags=["ingestion"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def ingest_transactions(request: IngestBatchRequest, current_user: User = Depends(get_current_user),  db:AsyncSession = Depends(get_db)):
    batch_id = uuid4()
    raw_records = []

    approved_source_id = resolve_source_id(current_user, request.source_id)

    result = await db.execute(select(Source).where(Source.id == approved_source_id))
    result = result.scalar_one_or_none()
    if result is None:
        raise HTTPException(status_code=404, detail="Source not found")
    
    for transaction in request.transactions:
        raw_record = RawTransaction(
            payload = transaction.model_dump(exclude_unset=True),
            source_id = approved_source_id,
            ingestion_batch = batch_id,
        )
        raw_records.append(raw_record)

    db.add_all(raw_records)
    await db.commit()

    return IngestResponse(status="success", batch_id=batch_id, processed_count=len(raw_records))