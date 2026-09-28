from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4


from app.db import get_db
from app.models import RawTransaction
from app.schemas.ingestion import IngestBatchRequest, IngestResponse

router = APIRouter(prefix="/api/v1/ingest", tags=["ingestion"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def ingest_transactions(request: IngestBatchRequest, db:AsyncSession = Depends(get_db)):
    batch_id = uuid4()
    raw_records = []
    for transaction in request.transactions:
        raw_record = RawTransaction(
            payload = transaction.model_dump(exclude_unset=True),
            source_id = request.source_id,
            ingestion_batch = batch_id,
        )
        raw_records.append(raw_record)

    db.add_all(raw_records)
    await db.commit()

    return IngestResponse(status="success", batch_id=batch_id, processed_count=len(raw_records))