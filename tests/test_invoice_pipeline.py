from pathlib import Path
import csv
from decimal import Decimal

from invoice_automation.extraction import extract_text_from_pdf
from invoice_automation.models import PurchaseOrder
from invoice_automation.parser import parse_invoice_text
from invoice_automation.reconciliation import reconcile_invoice


INCOMING_DIR = Path("data/incoming")
PO_FILE = Path("data/reference/purchase_orders.csv")


def load_purchase_orders() -> list[PurchaseOrder]:
    with PO_FILE.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        return [
            PurchaseOrder(
                po_number=row["po_number"],
                supplier_id=row["supplier_id"],
                currency=row["currency"],
                total=Decimal(row["total"]),
                status=row["status"],
            )
            for row in reader
        ]


def process_invoice(file_name: str):
    file_path = INCOMING_DIR / file_name

    text = extract_text_from_pdf(file_path)
    invoice = parse_invoice_text(text, file_name)

    purchase_orders = load_purchase_orders()

    return invoice, reconcile_invoice(invoice, purchase_orders)


def test_valid_invoice_end_to_end():
    invoice, result = process_invoice("INV-1001.pdf")

    assert invoice.invoice_number == "INV-1001"
    assert invoice.po_number == "PO-5001"
    assert invoice.total == Decimal("5980.00")

    assert result.matched is True
    assert result.issues == ()


def test_second_valid_invoice_end_to_end():
    invoice, result = process_invoice("INV-1002.pdf")

    assert invoice.invoice_number == "INV-1002"
    assert invoice.po_number == "PO-5002"

    assert result.matched is True
    assert result.issues == ()


def test_amount_mismatch_is_detected_end_to_end():
    invoice, result = process_invoice("INV-1003.pdf")

    assert invoice.invoice_number == "INV-1003"
    assert invoice.total == Decimal("1200.00")

    assert result.matched is False

    codes = {issue.code for issue in result.issues}

    assert "PO_AMOUNT_MISMATCH" in codes
    assert "PO_NOT_ACTIONABLE" in codes


def test_missing_po_is_detected_end_to_end():
    invoice, result = process_invoice("INV-1004.pdf")

    assert invoice.invoice_number == "INV-1004"
    assert invoice.po_number is None

    assert result.matched is False
    assert any(
        issue.code == "MISSING_PO"
        for issue in result.issues
    )


def test_fifth_invoice_matches_correct_po():
    invoice, result = process_invoice("INV-1005.pdf")

    assert invoice.invoice_number == "INV-1005"
    assert invoice.po_number == "PO-5004"

    assert result.matched is True
    assert result.issues == ()