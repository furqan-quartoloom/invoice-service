import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.database import init_db
from app.routers import invoices
from app.validation_errors import format_validation_errors

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Oracle Fusion Invoice API",
    description="Validates invoice payloads, forwards them to Oracle Fusion, and stores successful results.",
    version="1.0.0",
)

app.include_router(invoices.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _request: object, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=format_validation_errors(exc.errors()),
    )


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
