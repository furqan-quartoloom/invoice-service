import logging

from fastapi import FastAPI

from app.database import init_db
from app.routers import invoices

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Oracle Fusion Invoice API",
    description="Validates invoice payloads, forwards them to Oracle Fusion, and stores successful results.",
    version="1.0.0",
)

app.include_router(invoices.router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
