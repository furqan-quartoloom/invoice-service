from typing import Any

FIELD_LABELS: dict[str, str] = {
    "InvoiceNumber": "Invoice Number",
    "InvoiceCurrency": "Invoice Currency",
    "InvoiceAmount": "Invoice Amount",
    "InvoiceDate": "Invoice Date",
    "BusinessUnit": "Business Unit",
    "Supplier": "Supplier",
    "SupplierSite": "Supplier Site",
    "Description": "Description",
    "InvoiceGroup": "Invoice Group",
    "invoiceDff": "Invoice DFF (Approval)",
    "__FLEX_Context": "Approval (__FLEX_Context)",
    "invoiceLines": "Invoice Lines",
    "LineNumber": "Line Number",
    "LineAmount": "Line Amount",
    "AccountingDate": "Accounting Date",
    "DistributionCombination": "Distribution Combination",
    "invoiceLineDff": "Invoice Line DFF",
    "taxApplicableStatus": "Tax Applicable Status",
}

ERROR_MESSAGES: dict[str, str] = {
    "missing": "This field is required.",
    "string_type": "Must be a text value.",
    "int_type": "Must be a whole number.",
    "float_type": "Must be a number.",
    "bool_type": "Must be true or false.",
    "date_type": "Must be a valid date (YYYY-MM-DD).",
    "datetime_type": "Must be a valid date/time.",
    "list_type": "Must be a list/array.",
    "dict_type": "Must be an object.",
    "greater_than": "Must be greater than {gt}.",
    "greater_than_equal": "Must be at least {ge}.",
    "less_than": "Must be less than {lt}.",
    "too_short": "Cannot be empty.",
    "too_long": "Value is too long.",
    "json_invalid": "Request body must be valid JSON.",
}


def format_validation_errors(errors: list[dict[str, Any]]) -> dict[str, Any]:
    formatted: list[dict[str, str]] = []

    for error in errors:
        path = _format_field_path(tuple(error.get("loc", ())))
        field_name = _leaf_field_name(error.get("loc", ()))
        label = FIELD_LABELS.get(field_name, field_name)
        message = _format_error_message(error, label)

        formatted.append(
            {
                "field": field_name,
                "path": path,
                "label": label,
                "message": message,
                "code": _error_code(error.get("type", "invalid")),
            }
        )

    count = len(formatted)
    summary = (
        f"{count} field needs to be corrected before the invoice can be submitted."
        if count == 1
        else f"{count} fields need to be corrected before the invoice can be submitted."
    )

    return {
        "success": False,
        "error": "Invalid invoice payload",
        "message": summary,
        "errors": formatted,
    }


def _format_field_path(loc: tuple[Any, ...]) -> str:
    parts: list[str] = []
    for item in loc:
        if item == "body":
            continue
        if isinstance(item, int):
            if parts:
                parts[-1] = f"{parts[-1]}[{item}]"
            else:
                parts.append(f"[{item}]")
        else:
            parts.append(str(item))
    return ".".join(parts) if parts else "payload"


def _leaf_field_name(loc: tuple[Any, ...] | list[Any]) -> str:
    for item in reversed(loc):
        if isinstance(item, str) and item != "body":
            return item
    return "payload"


def _error_code(error_type: str) -> str:
    if error_type in {"missing", "json_invalid"}:
        return error_type
    if error_type.startswith("value_error"):
        return "invalid_value"
    if error_type in {"greater_than", "greater_than_equal", "less_than"}:
        return "out_of_range"
    if error_type in {"string_type", "int_type", "float_type", "date_type", "list_type"}:
        return "invalid_type"
    if error_type in {"too_short", "too_long"}:
        return error_type
    return "invalid"


def _format_error_message(error: dict[str, Any], label: str) -> str:
    error_type = error.get("type", "")
    ctx = error.get("ctx") or {}

    if error_type == "missing":
        return f"{label} is required."

    if error_type == "json_invalid":
        return "Request body must be valid JSON."

    if error_type.startswith("value_error"):
        raw = error.get("msg", "Invalid value.")
        if raw.startswith("Value error, "):
            raw = raw.removeprefix("Value error, ")
        return f"{label}: {raw}"

    template = ERROR_MESSAGES.get(error_type)
    if template:
        try:
            return f"{label}: {template.format(**ctx)}"
        except KeyError:
            return f"{label}: {template}"

    return f"{label}: {error.get('msg', 'Invalid value.')}"
