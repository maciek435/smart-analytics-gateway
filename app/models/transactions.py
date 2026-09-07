from sqlalchemy import ForeignKey, DateTime, func, false, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB, UUID
from datetime import datetime
from uuid import UUID as PyUUID
from decimal import Decimal

from app.db import Base


class RawTransaction(Base):
    __tablename__ = "raw_transactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ingestion_batch: Mapped[PyUUID | None] = mapped_column(UUID, nullable=True)
    processed: Mapped[bool] = mapped_column(server_default=false())

class CleanTransaction(Base):
    __tablename__ = "clean_transactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    raw_id: Mapped[int] = mapped_column(ForeignKey("raw_transactions.id"))
    external_ref: Mapped[str | None] = mapped_column(nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    transaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    quality_flag: Mapped[str] = mapped_column(String, server_default=text("'ok'"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
