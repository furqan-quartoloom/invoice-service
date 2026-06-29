import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

ORACLE_INVOICE_URL = os.getenv(
    "ORACLE_INVOICE_URL",
    "https://ecfz-test.fa.ap2.oraclecloud.com/fscmRestApi/resources/11.13.18.05/invoices",
)
ORACLE_USERNAME = os.getenv("ORACLE_USERNAME", "")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "")
REQUEST_TIMEOUT = float(os.getenv("ORACLE_REQUEST_TIMEOUT", "30"))
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "invoices.db")))
