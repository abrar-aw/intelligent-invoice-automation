from datetime import datetime
from decimal import Decimal, InvalidOperation

from invoice_automation.models import Invoice


class InvoiceParseError(Exception):
    """Raised when invoice text cannot be parsed into an Invoice."""


def _extract_field(text: str, field_name: str, required: bool = True) -> str | None:
    """Extract a labeled field from invoice text."""

    prefix = f"{field_name}:"

    for line in text.splitlines():
        line = line.strip()

        if line.lower().startswith(prefix.lower()):
            value = line[len(prefix):].strip()

            if value:
                return value

            if required:
                raise InvoiceParseError(
                    f"Required field '{field_name}' is empty"
                )

            return None

    if required:
        raise InvoiceParseError(
            f"Required field '{field_name}' not found"
        )

    return None


def _parse_date(value: str, field_name: str):
    """Parse an invoice date in DD/MM/YYYY format."""

    try:
        return datetime.strptime(value, "%d/%m/%Y").date()
    except ValueError as exc:
        raise InvoiceParseError(
            f"Invalid date for '{field_name}': {value}"
        ) from exc


def _parse_decimal(value: str, field_name: str) -> Decimal:
    """Parse a monetary value into Decimal."""

    try:
        return Decimal(value.replace(",", "").strip())
    except InvalidOperation as exc:
        raise InvoiceParseError(
            f"Invalid amount for '{field_name}': {value}"
        ) from exc


def parse_invoice_text(text: str, source_file: str) -> Invoice:
    """
    Parse extracted invoice text into an Invoice object.

    Required fields must be present and valid.
    Due date and PO number are optional.
    """

    if not text or not text.strip():
        raise InvoiceParseError("Invoice text is empty")

    invoice_number = _extract_field(text, "Invoice Number")
    supplier_id = _extract_field(text, "Supplier ID")
    supplier_name = _extract_field(text, "Supplier")
    invoice_date_value = _extract_field(text, "Invoice Date")
    due_date_value = _extract_field(
        text,
        "Due Date",
        required=False,
    )
    po_number = _extract_field(
        text,
        "PO Number",
        required=False,
    )
    currency = _extract_field(text, "Currency")
    subtotal_value = _extract_field(text, "Subtotal")
    tax_value = _extract_field(text, "Tax")
    total_value = _extract_field(text, "Total")

    invoice_date = _parse_date(
        invoice_date_value,
        "Invoice Date",
    )

    due_date = (
        _parse_date(due_date_value, "Due Date")
        if due_date_value
        else None
    )

    subtotal = _parse_decimal(
        subtotal_value,
        "Subtotal",
    )

    tax = _parse_decimal(
        tax_value,
        "Tax",
    )

    total = _parse_decimal(
        total_value,
        "Total",
    )

    return Invoice(
        invoice_number=invoice_number,
        supplier_id=supplier_id,
        supplier_name=supplier_name,
        invoice_date=invoice_date,
        due_date=due_date,
        po_number=po_number,
        currency=currency,
        subtotal=subtotal,
        tax=tax,
        total=total,
        source_file=source_file,
    )