from app.models.transactions import CleanTransaction


def source_id_filter(stmt, source_id):
    if source_id is not None:
        stmt = stmt.where(CleanTransaction.source_id == source_id)     
    return stmt

from datetime import datetime

def transaction_filters(
    stmt,
    currency: str | None = None,
    status: str | None = None,
    quality_flag: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
):
    if currency is not None:
        stmt = stmt.where(CleanTransaction.currency == currency.upper())
    if status is not None:
        stmt = stmt.where(CleanTransaction.status == status)
    if quality_flag is not None:
        stmt = stmt.where(CleanTransaction.quality_flag == quality_flag)
    if date_from is not None:
        stmt = stmt.where(CleanTransaction.transaction_date >= date_from)
    if date_to is not None:
        stmt = stmt.where(CleanTransaction.transaction_date <= date_to)
    return stmt