from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class InvoiceLineDffItem(BaseModel):
    taxApplicableStatus: str = Field(min_length=1)


class InvoiceLine(BaseModel):
    LineNumber: int = Field(ge=1)
    LineAmount: float = Field(gt=0)
    AccountingDate: date
    DistributionCombination: str = Field(min_length=1)
    invoiceLineDff: list[InvoiceLineDffItem] = Field(min_length=1)


class InvoiceDffItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    flex_context: str = Field(alias="__FLEX_Context", min_length=1)


class CreateInvoiceRequest(BaseModel):
    InvoiceNumber: str = Field(min_length=1)
    InvoiceCurrency: str = Field(min_length=1)
    InvoiceAmount: float = Field(gt=0)
    InvoiceDate: date
    BusinessUnit: str = Field(min_length=1)
    Supplier: str = Field(min_length=1)
    SupplierSite: str = Field(min_length=1)
    Description: str | None = None
    InvoiceGroup: str | None = None
    invoiceDff: list[InvoiceDffItem] = Field(min_length=1)
    invoiceLines: list[InvoiceLine] = Field(min_length=1)

    @field_validator("InvoiceGroup")
    @classmethod
    def reject_empty_invoice_group(cls, value: str | None) -> str | None:
        if value == "":
            raise ValueError("InvoiceGroup cannot be an empty string")
        return value

    @model_validator(mode="after")
    def validate_line_amounts(self) -> "CreateInvoiceRequest":
        line_total = sum(line.LineAmount for line in self.invoiceLines)
        if abs(line_total - self.InvoiceAmount) > 0.01:
            raise ValueError(
                f"InvoiceAmount ({self.InvoiceAmount}) must equal the sum of "
                f"line amounts ({line_total})"
            )
        return self

    def to_oracle_payload(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude_none=True, by_alias=True)
