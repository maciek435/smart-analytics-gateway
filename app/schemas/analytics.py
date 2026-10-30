from pydantic import BaseModel
from decimal import Decimal

class AnalyticsSummary(BaseModel):
    total_transactions: int
    total_volume_by_currency: dict[str, float]
    data_quality_score: float