import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import DATABASE_PATH


def init_db() -> None:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS invoice_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                invoice_number TEXT NOT NULL,
                business_unit TEXT NOT NULL,
                supplier TEXT NOT NULL,
                invoice_amount REAL NOT NULL,
                oracle_status INTEGER NOT NULL,
                request_payload TEXT NOT NULL,
                response_payload TEXT NOT NULL
            )
            """
        )


def save_successful_invoice(
    *,
    invoice_number: str,
    business_unit: str,
    supplier: str,
    invoice_amount: float,
    oracle_status: int,
    request_payload: dict[str, Any],
    response_payload: Any,
) -> int:
    created_at = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.execute(
            """
            INSERT INTO invoice_records (
                created_at,
                invoice_number,
                business_unit,
                supplier,
                invoice_amount,
                oracle_status,
                request_payload,
                response_payload
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                created_at,
                invoice_number,
                business_unit,
                supplier,
                invoice_amount,
                oracle_status,
                json.dumps(request_payload),
                json.dumps(response_payload),
            ),
        )
        return int(cursor.lastrowid)
