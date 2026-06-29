import logging
from typing import Any

import httpx

from app.config import (
    ORACLE_INVOICE_URL,
    ORACLE_PASSWORD,
    ORACLE_USERNAME,
    REQUEST_TIMEOUT,
)

logger = logging.getLogger(__name__)


class OracleConfigError(Exception):
    pass


class OracleTimeoutError(Exception):
    pass


class OracleConnectionError(Exception):
    pass


def parse_response_body(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return {"raw": response.text}


async def create_invoice(payload: dict[str, Any]) -> httpx.Response:
    """Forward the caller payload to Oracle Fusion invoice create API."""
    if not ORACLE_USERNAME or not ORACLE_PASSWORD:
        raise OracleConfigError("Oracle credentials not configured in .env")

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.post(
                ORACLE_INVOICE_URL,
                json=payload,
                auth=(ORACLE_USERNAME, ORACLE_PASSWORD),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
    except httpx.TimeoutException as exc:
        logger.error("Oracle API request timed out after %ss", REQUEST_TIMEOUT)
        raise OracleTimeoutError("Oracle API request timed out") from exc
    except httpx.RequestError as exc:
        logger.error("Oracle API request failed: %s", exc)
        raise OracleConnectionError("Failed to reach Oracle API") from exc

    logger.info(
        "Oracle response status=%s body=%s",
        response.status_code,
        response.text,
    )
    return response
