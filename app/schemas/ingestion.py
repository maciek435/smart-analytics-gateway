from pydantic import BaseModel, ConfigDict
from uuid import UUID as PyUUID
from typing import Literal, Any

class TransactionPayload(BaseModel):
    external_ref: Any = None
    amount: Any = None
    currency: Any = None
    timestamp: Any = None
    model_config = ConfigDict(extra="allow")

class IngestBatchRequest(BaseModel):
    source_id : int
    transactions: list[TransactionPayload]

class IngestResponse(BaseModel):
    status: Literal["success"]
    batch_id: PyUUID
    processed_count: int