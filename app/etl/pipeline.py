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

def validate_amount(df):
    df["issue_type"] = None
    df["issue_detail"] = None

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    invalid_amount_mask = (df["amount"] < 0) | (df["amount"] == 0) | (df["amount"].isna())

    df.loc[invalid_amount_mask, "issue_type"] = "invalid_amount"
    df.loc[invalid_amount_mask, "issue_detail"] = "Amount is missing, zero, or negative"




    return df
