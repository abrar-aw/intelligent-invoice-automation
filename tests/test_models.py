from datetime import date
from decimal import Decimal

import pytest

from invoice_automation.models import Invoice


def make_invoice(**overrides):
    data = {
        "invoice_number": "INV-1001",
        "supplier_id": "SUP-001",
        "supplier_name": "ABC Supplies Ltd.",
        "invoice_date": date(2026, 9, 18),
        "due_date": date(2026, 10, 18),
        "po_number": "PO-5001",
        "currency": "USD",
        "subtotal": Decimal("1000.00"),
        "tax": Decimal("150.00"),
        "total": Decimal("1150.00"),
        "source_file": "invoice_1001.pdf",
    }

    data.update(overrides)
    return Invoice(**data)


def test_create_invoice():
    invoice = make_invoice()

    assert invoice.invoice_number == "INV-1001"
    assert invoice.supplier_id == "SUP-001"
    assert invoice.supplier_name == "ABC Supplies Ltd."
    assert invoice.total == Decimal("1150.00")
    assert invoice.source_file == "invoice_1001.pdf"


def test_invoice_can_have_missing_due_date_and_po():
    invoice = make_invoice(
        due_date=None,
        po_number=None,
    )

    assert invoice.due_date is None
    assert invoice.po_number is None


def test_invoice_stores_decimal_amounts():
    invoice = make_invoice(
        subtotal=Decimal("100.25"),
        tax=Decimal("15.04"),
        total=Decimal("115.29"),
    )

    assert invoice.subtotal == Decimal("100.25")
    assert invoice.tax == Decimal("15.04")
    assert invoice.total == Decimal("115.29")


def test_invoice_preserves_source_file():
    invoice = make_invoice(
        source_file="incoming/INV-2026-0042.pdf",
    )

    assert invoice.source_file == "incoming/INV-2026-0042.pdf"