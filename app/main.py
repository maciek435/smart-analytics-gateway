from fastapi import FastAPI
from app.ingestion.router import router as ingestion_router


app = FastAPI(
    title="Smart Analytics & API Gateway",
    description="System przyjmujący transakcje, czyszczący je (ETL) i serwujący przez API.",
    version="0.1.0",
)

app.include_router(ingestion_router)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API Gateway is running"}