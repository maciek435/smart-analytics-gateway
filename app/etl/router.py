from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.etl.pipeline import run_etl_pipeline
from app.schemas.etl import ETLRunResponse

router = APIRouter(prefix="/api/v1/etl", tags=["etl"])

@router.post("/run", response_model=ETLRunResponse)
async def trigger_etl(db:AsyncSession = Depends(get_db)):
    result = await run_etl_pipeline(db)
    response = ETLRunResponse(
        status="completed",
        clean_count=result["clean_count"],
        error_count=result["error_count"]

    )
    return response