from datetime import date
from decimal import Decimal

from invoice_automation.models import Invoice, PurchaseOrder
from invoice_automation.reconciliation import reconcile_invoice


def make_invoice(**overrides):
    data = {
        "invoice_number": "INV-1001",
        "supplier_id": "SUP-001",
        "supplier_name": "ABC Supplies Ltd.",
        "invoice_date": date(2026, 9, 18),
        "due_date": date(2026, 10, 18),
        "po_number": "PO-5001",
        "currency": "USD",
        "subtotal": Decimal("5200.00"),
        "tax": Decimal("780.00"),
        "total": Decimal("5980.00"),
        "source_file": "INV-1001.pdf",
    }

    data.update(overrides)
    return Invoice(**data)


def make_po(**overrides):
    data = {
        "po_number": "PO-5001",
        "supplier_id": "SUP-001",
        "currency": "USD",
        "total": Decimal("5980.00"),
        "status": "APPROVED",
    }

    data.update(overrides)
    return PurchaseOrder(**data)


def test_matching_invoice_and_po():
    invoice = make_invoice()
    po = make_po()

    result = reconcile_invoice(invoice, [po])

    assert result.matched is True
    assert result.po_number == "PO-5001"
    assert result.issues == ()


def test_missing_po_is_reported():
    invoice = make_invoice(po_number="PO-9999")
    po = make_po()

    result = reconcile_invoice(invoice, [po])

    assert result.matched is False
    assert any(issue.code == "PO_NOT_FOUND" for issue in result.issues)


def test_supplier_mismatch_is_reported():
    invoice = make_invoice()
    po = make_po(supplier_id="SUP-999")

    result = reconcile_invoice(invoice, [po])

    assert result.matched is False
    assert any(
        issue.code == "SUPPLIER_MISMATCH"
        for issue in result.issues
    )


def test_currency_mismatch_is_reported():
    invoice = make_invoice(currency="EUR")
    po = make_po()

    result = reconcile_invoice(invoice, [po])

    assert result.matched is False
    assert any(
        issue.code == "CURRENCY_MISMATCH"
        for issue in result.issues
    )


def test_amount_mismatch_is_reported():
    invoice = make_invoice(total=Decimal("6000.00"))
    po = make_po()

    result = reconcile_invoice(invoice, [po])

    assert result.matched is False
    assert any(
        issue.code == "PO_AMOUNT_MISMATCH"
        for issue in result.issues
    )


def test_closed_po_is_not_actionable():
    invoice = make_invoice()
    po = make_po(status="CLOSED")

    result = reconcile_invoice(invoice, [po])

    assert result.matched is False
    assert any(
        issue.code == "PO_NOT_ACTIONABLE"
        for issue in result.issues
    )


def test_multiple_reconciliation_errors_are_reported():
    invoice = make_invoice(
        supplier_id="SUP-999",
        currency="EUR",
        total=Decimal("6000.00"),
    )

    po = make_po(
        supplier_id="SUP-001",
        currency="USD",
        total=Decimal("5980.00"),
    )

    result = reconcile_invoice(invoice, [po])

    assert result.matched is False

    codes = {issue.code for issue in result.issues}

    assert "SUPPLIER_MISMATCH" in codes
    assert "CURRENCY_MISMATCH" in codes
    assert "PO_AMOUNT_MISMATCH" in codes


def test_invoice_without_po_is_not_matched():
    invoice = make_invoice(po_number=None)

    result = reconcile_invoice(invoice, [make_po()])

    assert result.matched is False
    assert any(issue.code == "MISSING_PO" for issue in result.issues)