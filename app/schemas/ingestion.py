from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime
from uuid import UUID as PyUUID
from typing import Literal

class TransactionPayload(BaseModel):
    external_ref: str | None = None
    amount: Decimal | None = None
    currency: str | None = None
    timestamp: datetime | None = None
    model_config = ConfigDict(extra="allow")


class IngestBatchRequest(BaseModel):
    source_id : int
    transactions: list[TransactionPayload]

class IngestResponse(BaseModel):
    status: Literal["success"]
    batch_id: PyUUID
    processed_count: int