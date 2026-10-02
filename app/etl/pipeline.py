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

def validate_currency(df):
    df["currency"] = df["currency"].str.strip().str.upper()

    invalid_currency_mask = (df["currency"].isna()) | (df["currency"].str.len() != 3)
    df.loc[invalid_currency_mask, "issue_type"] = "invalid_currency"
    df.loc[invalid_currency_mask, "issue_detail"] = "Currency is missing or not 3 characters long"

    return df

def validate_external_ref(df):
    df["external_ref"] = df["external_ref"].str.strip()
    missing_ref_mask = (df["external_ref"].isna())
    df.loc[missing_ref_mask, "external_ref"] = "GENERATED-" + df["raw_id"].astype(str)

    return df

