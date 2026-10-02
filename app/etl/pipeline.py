import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from decimal import Decimal

from app.models.transactions import CleanTransaction
from app.models.quality import DataQualityIssue
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

async def load_transformed_data(df, db: AsyncSession):
    
    processed_raw_ids = df["raw_id"].tolist()

    clean_df = df[df["issue_type"].isna()]
    error_df = df[df["issue_type"].notna()]

    clean_records = []
    for _, row in clean_df.iterrows():
        clean_record = CleanTransaction(
            raw_id = row["raw_id"],
            amount = Decimal(str(row["amount"])),
            currency = row["currency"],
            transaction_date = row["timestamp"],
            source_id  = row["source_id"],
            quality_flag = "ok",
        )
        clean_records.append(clean_record)

    error_records = []
    for _, row in error_df.iterrows():
        error_record = DataQualityIssue(
            raw_id = row["raw_id"],
            issue_type = row["issue_type"],
            detail = row["issue_detail"],
        )

        error_records.append(error_record)

    db.add_all(clean_records)
    db.add_all(error_records)

    stmt = (
        update(RawTransaction)
        .where(RawTransaction.id.in_(processed_raw_ids))
        .values(processed=True)
    )
    await db.execute(stmt)
    await db.commit()

    return len(clean_records), len(error_records)



