from datetime import date
from decimal import Decimal

from invoice_automation.models import Invoice, PurchaseOrder
from invoice_automation.validators import reconcile_with_po, validate_invoice


def invoice(**overrides):
    values = dict(
        invoice_number="INV-1001",
        supplier_id="SUP-001",
        supplier_name="Acme Supplies",
        invoice_date=date(2026, 9, 1),
        due_date=date(2026, 10, 1),
        po_number="PO-5001",
        currency="USD",
        subtotal=Decimal("100.00"),
        tax=Decimal("15.00"),
        total=Decimal("115.00"),
        source_file="invoice.pdf",
    )
    values.update(overrides)
    return Invoice(**values)


def po(**overrides):
    values = dict(
        po_number="PO-5001",
        supplier_id="SUP-001",
        currency="USD",
        total=Decimal("115.00"),
    )
    values.update(overrides)
    return PurchaseOrder(**values)


def test_valid_invoice_has_no_issues():
    assert validate_invoice(invoice()) == []


def test_total_mismatch_is_detected():
    issues = validate_invoice(invoice(total=Decimal("120.00")))
    assert any(i.code == "TOTAL_MISMATCH" for i in issues)


def test_missing_po_is_detected():
    issues = reconcile_with_po(invoice(po_number=None), None)
    assert issues[0].code == "MISSING_PO"


def test_po_amount_mismatch_is_detected():
    issues = reconcile_with_po(invoice(), po(total=Decimal("200.00")))
    assert any(i.code == "PO_AMOUNT_MISMATCH" for i in issues)
