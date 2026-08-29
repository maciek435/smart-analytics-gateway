from fastapi import FastAPI

app = FastAPI(
    title="Smart Analytics & API Gateway",
    description="System przyjmujący transakcje, czyszczący je (ETL) i serwujący przez API.",
    version="0.1.0",
)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API Gateway is running"}