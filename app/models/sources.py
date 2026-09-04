from app.db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import true

class Source(Base):
    __tablename__ = "sources"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    schema_version: Mapped[str | None] = mapped_column(nullable=True)
    active: Mapped[bool] = mapped_column(server_default=true())

    