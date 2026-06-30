# Oracle Fusion Invoice API

A small **FastAPI service** that validates Oracle Fusion invoice payloads, forwards them to the Oracle Fusion REST API, and stores successful results in SQLite.

---

## 🚀 Features

- ✅ **Pydantic validation** before calling Oracle  
  - Invalid payloads return `422`

- ✅ **Single Oracle API call**
  - Payload is validated and forwarded as-is

- ✅ **SQLite persistence**
  - Stores successful invoice creation requests and responses

- ✅ **Docker support**
  - Easy local and deployment setup

---

## 📁 Project Structure

```text
app/
├── main.py              # FastAPI application
├── config.py            # Environment configuration
├── database.py          # SQLite initialization & persistence
├── schemas/
│   └── invoice.py       # Request validation models
├── routers/
│   └── invoices.py      # Invoice API routes
└── services/
    └── oracle_client.py # Oracle HTTP client

samples/
└── invoice_payload_sample.json

data/
└── invoices.db          # Created automatically
```

---

## 🛠 Requirements

- Python **3.12+**
- Docker & Docker Compose (optional)
- Oracle Fusion test credentials

---

## ⚙️ Configuration

Create your environment file:

```bash
cp .env.example .env
```

Update values:

| Variable | Description |
|---|---|
| `ORACLE_USERNAME` | Oracle Fusion username |
| `ORACLE_PASSWORD` | Oracle Fusion password |
| `ORACLE_INVOICE_URL` | Oracle Fusion invoice REST endpoint |
| `ORACLE_REQUEST_TIMEOUT` | Request timeout (default: 30s) |
| `DATABASE_PATH` | SQLite database path |

Example:

```env
ORACLE_USERNAME=my_user
ORACLE_PASSWORD=my_password
ORACLE_INVOICE_URL=https://oracle-endpoint/invoices
DATABASE_PATH=data/invoices.db
```

---

# ▶️ Run Locally

Create virtual environment:

```bash
python -m venv venv
```

Activate:

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start API:

```bash
uvicorn app.main:app --reload
```

API:

```
http://127.0.0.1:8000
```

Swagger docs:

```
http://127.0.0.1:8000/docs
```

---

# 🐳 Run With Docker

Create environment file:

```bash
cp .env.example .env
```

Build and start:

```bash
docker compose up --build
```

API:

```
http://localhost:8000
```

SQLite data persists using Docker volume.

---

## Docker Commands

Run background:

```bash
docker compose up -d --build
```

View logs:

```bash
docker compose logs -f api
```

Stop:

```bash
docker compose down
```

---

# 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/create-invoice` | Validate and create invoice |

---

# 📦 Create Invoice Request

The client must send a complete Oracle-ready JSON payload.

Example:

```bash
curl -X POST http://localhost:8000/create-invoice \
-H "Content-Type: application/json" \
-d @samples/invoice_payload_sample.json
```

---

## Validation Rules

Important payload rules:

- `invoiceDff` must be an array:

```json
[
  {
    "__FLEX_Context": "value"
  }
]
```

- `invoiceLineDff` must exist inside each invoice line

- `InvoiceAmount` must equal the sum of invoice line amounts

- Do not send empty strings:

❌

```json
{
  "InvoiceGroup": ""
}
```

---

# 🔄 Request Flow

```text
Client
  |
  | POST /create-invoice
  |
  v
Pydantic Validation
  |
  | invalid
  v
422 Response

  |
  | valid
  v

Oracle Fusion API
  |
  | success
  v

Save to SQLite
  |
  v

Return Oracle Response
```

---

# 🗄 SQLite Storage

Successful Oracle responses (`2xx`) are stored.

Table:

`invoice_records`

| Column | Description |
|---|---|
| id | Auto increment ID |
| created_at | UTC timestamp |
| invoice_number | Invoice number |
| business_unit | Business unit |
| supplier | Supplier name |
| invoice_amount | Invoice total |
| oracle_status | Oracle HTTP status |
| request_payload | Original request JSON |
| response_payload | Oracle response JSON |

Failed Oracle requests are not stored.

---

# ❌ Error Responses

## Validation errors (`422`)

When the payload fails local validation:

```json
{
  "success": false,
  "error": "Invalid invoice payload",
  "message": "2 fields need to be corrected before the invoice can be submitted.",
  "errors": [
    {
      "field": "Supplier",
      "path": "Supplier",
      "label": "Supplier",
      "message": "Supplier is required.",
      "code": "missing"
    }
  ]
}
```

| Field | Use in UI |
|---|---|
| `message` | Top-level alert text |
| `errors[].label` | Human-readable field name |
| `errors[].message` | Field-level error message |
| `errors[].path` | Form field path (e.g. `invoiceLines[0].LineAmount`) |
| `errors[].code` | `missing`, `invalid_value`, `invalid_type`, `out_of_range` |

## Other errors

| Status | Meaning |
|---|---|
| `401` | Oracle authentication failed |
| `502` | Oracle unavailable |
| `504` | Oracle timeout |
| `4xx/5xx` | Oracle API error |

---

## 📌 Tech Stack

- FastAPI
- Pydantic
- SQLite
- Docker
- Oracle Fusion REST API

---