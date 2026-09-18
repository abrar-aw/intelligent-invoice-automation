from datetime import datetime
from decimal import Decimal, InvalidOperation

from invoice_automation.models import Invoice


class InvoiceParseError(Exception):
    """Raised when invoice text cannot be parsed into an Invoice."""


KNOWN_FIELDS = {
    "Invoice Number",
    "Supplier ID",
    "Supplier",
    "Invoice Date",
    "Due Date",
    "PO Number",
    "Currency",
    "Subtotal",
    "Tax",
    "Total",
}

def _extract_supplier_name(text: str) -> str:
    """
    Extract supplier name from the invoice.

    Supports both:
        Supplier: ABC Supplies Ltd.

    and the generated PDF layout where the supplier name
    appears as the first non-empty line.
    """

    labeled_supplier = _extract_field(
        text,
        "Supplier",
        required=False,
    )

    if labeled_supplier:
        return labeled_supplier

    for line in text.splitlines():
        line = line.strip()

        if line:
            return line

    raise InvoiceParseError("Supplier name not found")

def _extract_field(
    text: str,
    field_name: str,
    required: bool = True,
    aliases: tuple[str, ...] = (),
) -> str | None:
    """Extract a labeled field from invoice text."""

    lines = [line.strip() for line in text.splitlines()]
    field_names = (field_name, *aliases)

    for index, line in enumerate(lines):
        # Format: "Field: Value"
        for current_field in field_names:
            prefix = f"{current_field}:"

            if line.lower().startswith(prefix.lower()):
                value = line[len(prefix):].strip()

                if value:
                    return value

                if required:
                    raise InvoiceParseError(
                        f"Required field '{field_name}' is empty"
                    )

                return None

        # Format: "Field" followed by "Value"
        if any(
            line.lower() == current_field.lower()
            for current_field in field_names
        ):
            if index + 1 >= len(lines):
                if required:
                    raise InvoiceParseError(
                        f"Required field '{field_name}' is empty"
                    )
                return None

            next_line = lines[index + 1]

            if not next_line:
                if required:
                    raise InvoiceParseError(
                        f"Required field '{field_name}' is empty"
                    )
                return None

            if next_line.lower() in {
                field.lower()
                for field in KNOWN_FIELDS
            }:
                if required:
                    raise InvoiceParseError(
                        f"Required field '{field_name}' is empty"
                    )
                return None

            return next_line

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
    supplier_name = _extract_supplier_name(text)
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
        aliases=("Purchase Order",),
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