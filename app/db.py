from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import json
from decimal import Decimal
from datetime import datetime

from app.config import settings

class Base(DeclarativeBase):
    pass

def custom_json_serializer(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

engine = create_async_engine(settings.database_url, echo=True, json_serializer=lambda obj: json.dumps(obj, default=custom_json_serializer))

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
