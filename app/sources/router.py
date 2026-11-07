from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import require_admin
from app.db import get_db
from app.models import Source
from app.schemas.sources import SourceCreate, SourceResponse

router = APIRouter(prefix="/api/v1/sources", tags=["sources"])


@router.post("", response_model=SourceResponse, status_code=201,
             dependencies=[Depends(require_admin)])
async def create_source(body: SourceCreate, db: AsyncSession = Depends(get_db)):
    existing = (
        await db.execute(select(Source).where(Source.name == body.name))
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=409, detail="Source name already exists")

    source = Source(name=body.name, schema_version=body.schema_version)
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source


@router.get("", response_model=list[SourceResponse],
            dependencies=[Depends(require_admin)])
async def list_sources(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Source).order_by(Source.id))
    return result.scalars().all()