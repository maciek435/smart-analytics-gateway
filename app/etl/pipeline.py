import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import RawTransaction

async def extract_raw_transactions(db: AsyncSession):
    stmt = select(RawTransaction).where(RawTransaction.processed == False)
    result = await db.execute(stmt)
    raw_records = result.scalars().all()
    if not raw_records:
        return None

    payloads = [record.payload for record in raw_records]

    df = pd.DataFrame(payloads)
    df["raw_id"] = [record.id for record in raw_records]
    df["source_id"] = [record.source_id for record in raw_records]

    return df


