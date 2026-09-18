from datetime import date
from decimal import Decimal

from invoice_automation.duplicates import is_duplicate
from invoice_automation.models import Invoice


def make_invoice(
    invoice_number: str = "INV-1001",
    supplier_id: str = "SUP-001",
) -> Invoice:
    return Invoice(
        invoice_number=invoice_number,
        supplier_id=supplier_id,
        supplier_name="ABC Supplies Ltd.",
        invoice_date=date(2026, 9, 18),
        due_date=date(2026, 10, 18),
        po_number="PO-5001",
        currency="USD",
        subtotal=Decimal("5200.00"),
        tax=Decimal("780.00"),
        total=Decimal("5980.00"),
        source_file="invoice.pdf",
    )


def test_invoice_is_not_duplicate_when_no_previous_invoices_exist():
    invoice = make_invoice()

    assert is_duplicate(invoice, []) is False


def test_invoice_is_duplicate_when_invoice_number_and_supplier_match():
    invoice = make_invoice()

    previous_invoice = make_invoice()

    assert is_duplicate(invoice, [previous_invoice]) is True


def test_same_invoice_number_from_different_supplier_is_not_duplicate():
    invoice = make_invoice(supplier_id="SUP-001")

    previous_invoice = make_invoice(supplier_id="SUP-002")

    assert is_duplicate(invoice, [previous_invoice]) is False


def test_different_invoice_number_from_same_supplier_is_not_duplicate():
    invoice = make_invoice(invoice_number="INV-1001")

    previous_invoice = make_invoice(invoice_number="INV-1002")

    assert is_duplicate(invoice, [previous_invoice]) is False