import logging

from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

from app.database import save_successful_invoice
from app.schemas.invoice import CreateInvoiceRequest
from app.services.oracle_client import (
    OracleConfigError,
    OracleConnectionError,
    OracleTimeoutError,
    create_invoice,
    parse_response_body,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["invoices"])


@router.post("/create-invoice")
async def create_invoice_endpoint(payload: CreateInvoiceRequest) -> Response:
    oracle_payload = payload.to_oracle_payload()
    logger.info("Validated invoice request: %s", payload.InvoiceNumber)

    try:
        oracle_response = await create_invoice(oracle_payload)
    except OracleConfigError as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})
    except OracleTimeoutError as exc:
        return JSONResponse(status_code=504, content={"error": str(exc)})
    except OracleConnectionError as exc:
        return JSONResponse(status_code=502, content={"error": str(exc)})

    response_body = parse_response_body(oracle_response)

    if oracle_response.status_code == 401:
        return JSONResponse(
            status_code=401,
            content={
                "error": "Oracle authentication failed",
                "detail": response_body,
            },
        )

    if 200 <= oracle_response.status_code < 300:
        record_id = save_successful_invoice(
            invoice_number=payload.InvoiceNumber,
            business_unit=payload.BusinessUnit,
            supplier=payload.Supplier,
            invoice_amount=payload.InvoiceAmount,
            oracle_status=oracle_response.status_code,
            request_payload=oracle_payload,
            response_payload=response_body,
        )
        logger.info("Saved successful invoice record id=%s", record_id)

    return JSONResponse(
        status_code=oracle_response.status_code,
        content=response_body,
    )
