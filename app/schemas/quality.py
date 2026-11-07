from datetime import datetime
from typing import Any

from pydantic import BaseModel


class IssueResponse(BaseModel):
    id: int
    issue_type: str
    detail: str | None
    detected_at: datetime

    model_config = {"from_attributes": True}


class RejectedTransactionResponse(BaseModel):
    raw_id: int
    source_id: int
    payload: dict[str, Any]
    received_at: datetime
    issues: list[IssueResponse]


class RejectedTransactionListResponse(BaseModel):
    items: list[RejectedTransactionResponse]
    total: int
    limit: int
    offset: int