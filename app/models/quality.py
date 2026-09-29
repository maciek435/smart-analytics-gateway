from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String, Text, DateTime, func
from datetime import datetime

from app.db import Base

class DataQualityIssue(Base):
    __tablename__ = "data_quality_issues"
    id: Mapped[int] = mapped_column(primary_key=True) 
    raw_id: Mapped[int] = mapped_column(ForeignKey("raw_transactions.id"))
    issue_type: Mapped[str] = mapped_column(String, nullable=False)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
