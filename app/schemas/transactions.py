from datetime import datetime

from pydantic import BaseModel


class TransactionResponse(BaseModel):
    id: int
    raw_id: int
    external_ref: str | None
    amount: float
    currency: str
    transaction_date: datetime
    status: str
    source_id: int
    quality_flag: str
    created_at: datetime

    model_config = {"from_attributes": True}

class TransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    total: int
    limit: int
    offset: int

    model_config = {"from_attributes": True}