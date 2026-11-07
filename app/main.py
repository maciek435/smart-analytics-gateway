from fastapi import FastAPI
from app.ingestion.router import router as ingestion_router
from app.etl.router import router as etl_router
from app.serving.router import router as serving_router
from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.transactions.router import router as transactions_router
from app.quality.router import router as quality_router

app = FastAPI(
    title="Smart Analytics & API Gateway",
    description="System przyjmujący transakcje, czyszczący je (ETL) i serwujący przez API.",
    version="0.1.0",
)

app.include_router(ingestion_router)
app.include_router(etl_router)
app.include_router(serving_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(transactions_router)
app.include_router(quality_router)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API Gateway is running"}