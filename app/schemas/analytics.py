from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from typing import Literal

class AnalyticsSummary(BaseModel):
    total_transactions: int
    total_volume_by_currency: dict[str, float]
    data_quality_score: float

class TimeseriesPoint(BaseModel):
    period: datetime
    currency: str
    transactions: int
    volume: float

class RejectedPoint(BaseModel):
    period: datetime
    rejected: int

class TimeseriesResponse(BaseModel):
    group_by: Literal["day", "week", "month"]
    points: list[TimeseriesPoint]
    rejected: list[RejectedPoint]