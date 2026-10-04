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

    for col in ["amount", "currency", "external_ref", "timestamp", "status"]:
        if col not in df.columns:
            df[col] = None

    return df

def validate_amount(df):
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    invalid_amount_mask = (df["amount"] < 0) | (df["amount"] == 0) | (df["amount"].isna())
    invalid_rows = df[invalid_amount_mask]

    issues = []
    for _, row in invalid_rows.iterrows():
        issues.append({
            "raw_id": row["raw_id"],
            "issue_type": "invalid_amount",
            "detail": "Amount is missing, zero, or negaive",
        })

    return df, issues

def validate_currency(df):
    df["currency"] = df["currency"].str.strip().str.upper()

    invalid_currency_mask = (df["currency"].isna()) | (df["currency"].str.len() != 3)
    invalid_rows = df[invalid_currency_mask]

    issues = []
    for _, row in invalid_rows.iterrows():
        issues.append({
            "raw_id": row["raw_id"],
            "issue_type": "invalid_currency",
            "detail": "Currency is missing or not 3 characters long",
        })

    return df, issues

def validate_external_ref(df):
    df["external_ref"] = df["external_ref"].str.strip()
    missing_ref_mask = (df["external_ref"].isna())
    missing_rows = df[missing_ref_mask]
    issues = []
    for _, row in missing_rows.iterrows():
        issues.append({
            "raw_id": row["raw_id"],
            "issue_type": "generated_external_ref",
            "detail": "external_ref was missing, generated a temporary one",
        })

    df.loc[missing_ref_mask, "external_ref"] = "GENERATED-" + df["raw_id"].astype(str)

    return df, issues

def validate_timestamp(df):
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)

    invalid_timestamp_mask = df["timestamp"].isna()
    invalid_rows = df[invalid_timestamp_mask]

    issues = []
    for _, row in invalid_rows.iterrows():
        issues.append({
            "raw_id": row["raw_id"],
            "issue_type": "invalid_timestamp",
            "detail": "Timestamp is missing or invalid",
        })

    return df, issues

async def load_transformed_data(df, issues, db: AsyncSession):
    
    processed_raw_ids = df["raw_id"].tolist()

    blocking_types = {"invalid_amount", "invalid_currency", "invalid_timestamp"}
    blocked_raw_ids = {issue["raw_id"] for issue in issues if issue["issue_type"] in blocking_types}

    clean_df = df[~df["raw_id"].isin(blocked_raw_ids)]

    clean_records = []
    for _, row in clean_df.iterrows():
        clean_record = CleanTransaction(
            raw_id = row["raw_id"],
            amount = Decimal(str(row["amount"])),
            currency = row["currency"],
            transaction_date = row["timestamp"],
            source_id  = row["source_id"],
            external_ref = row["external_ref"],
            quality_flag = "ok",
            status = row.get("status") if pd.notna(row.get("status")) else "unknown",
        )
        clean_records.append(clean_record)

    error_records = [
        DataQualityIssue(
            raw_id = issue["raw_id"],
            issue_type = issue["issue_type"],
            detail = issue["detail"],
        )
        for issue in issues
    ]

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

async def run_etl_pipeline(db: AsyncSession):
    df = await extract_raw_transactions(db)
    if df is None:
        return{"message": "No new transactions to process"}

    df, issues_amount = validate_amount(df)
    df, issues_currency  = validate_currency(df)
    df, issues_ref  = validate_external_ref(df)
    df, issues_timestamp = validate_timestamp(df)

    issues = issues_amount + issues_currency + issues_ref + issues_timestamp

    clean_count, error_count = await load_transformed_data(df, issues, db)

    return {"clean_count": clean_count, "error_count": error_count}

