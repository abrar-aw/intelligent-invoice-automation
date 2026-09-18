from pathlib import Path
import csv
from decimal import Decimal

from invoice_automation.extraction import extract_text_from_pdf
from invoice_automation.models import ProcessingStatus, PurchaseOrder
from invoice_automation.parser import parse_invoice_text
from invoice_automation.reconciliation import reconcile_invoice
from invoice_automation.repository import InvoiceRepository


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


def process_invoice(
    file_name: str,
    repository: InvoiceRepository,
):
    file_path = INCOMING_DIR / file_name

    text = extract_text_from_pdf(file_path)
    invoice = parse_invoice_text(text, file_name)

    previous_record = repository.find_by_invoice(
        invoice.supplier_id,
        invoice.invoice_number,
    )

    if previous_record is not None:
        from invoice_automation.models import ProcessingResult

        return invoice, ProcessingResult(
            invoice_number=invoice.invoice_number,
            status=ProcessingStatus.DUPLICATE,
        )

    purchase_orders = load_purchase_orders()

    reconciliation = reconcile_invoice(
        invoice,
        purchase_orders,
    )

    status = (
        ProcessingStatus.PROCESSED
        if reconciliation.matched
        else ProcessingStatus.EXCEPTION
    )

    repository.save(invoice, status)

    from invoice_automation.models import ProcessingResult

    return invoice, ProcessingResult(
        invoice_number=invoice.invoice_number,
        status=status,
        issues=reconciliation.issues,
    )


def test_valid_invoice_end_to_end(tmp_path):
    repository = InvoiceRepository(tmp_path / "test.db")

    invoice, result = process_invoice(
        "INV-1001.pdf",
        repository,
    )

    assert invoice.invoice_number == "INV-1001"
    assert invoice.po_number == "PO-5001"
    assert invoice.total == Decimal("5980.00")

    assert result.status == ProcessingStatus.PROCESSED
    assert result.issues == ()


def test_second_valid_invoice_end_to_end(tmp_path):
    repository = InvoiceRepository(tmp_path / "test.db")

    invoice, result = process_invoice(
        "INV-1002.pdf",
        repository,
    )

    assert invoice.invoice_number == "INV-1002"
    assert invoice.po_number == "PO-5002"

    assert result.status == ProcessingStatus.PROCESSED
    assert result.issues == ()


def test_amount_mismatch_is_detected_end_to_end(tmp_path):
    repository = InvoiceRepository(tmp_path / "test.db")

    invoice, result = process_invoice(
        "INV-1003.pdf",
        repository,
    )

    assert invoice.invoice_number == "INV-1003"
    assert invoice.total == Decimal("1200.00")

    assert result.status == ProcessingStatus.EXCEPTION

    codes = {issue.code for issue in result.issues}

    assert "PO_AMOUNT_MISMATCH" in codes
    assert "PO_NOT_ACTIONABLE" in codes


def test_missing_po_is_detected_end_to_end(tmp_path):
    repository = InvoiceRepository(tmp_path / "test.db")

    invoice, result = process_invoice(
        "INV-1004.pdf",
        repository,
    )

    assert invoice.invoice_number == "INV-1004"
    assert invoice.po_number is None

    assert result.status == ProcessingStatus.EXCEPTION
    assert any(
        issue.code == "MISSING_PO"
        for issue in result.issues
    )


def test_fifth_invoice_matches_correct_po(tmp_path):
    repository = InvoiceRepository(tmp_path / "test.db")

    invoice, result = process_invoice(
        "INV-1005.pdf",
        repository,
    )

    assert invoice.invoice_number == "INV-1005"
    assert invoice.po_number == "PO-5004"

    assert result.status == ProcessingStatus.PROCESSED
    assert result.issues == ()


def test_invoice_is_duplicate_when_already_processed(tmp_path):
    repository = InvoiceRepository(tmp_path / "test.db")

    invoice, _ = process_invoice(
        "INV-1001.pdf",
        repository,
    )

    previous_record = repository.find_by_invoice(
        invoice.supplier_id,
        invoice.invoice_number,
    )

    assert previous_record is not None


def test_invoice_is_not_duplicate_when_not_previously_processed(tmp_path):
    repository = InvoiceRepository(tmp_path / "test.db")

    invoice, _ = process_invoice(
        "INV-1001.pdf",
        repository,
    )

    previous_record = repository.find_by_invoice(
        "SUP-999",
        "INV-9999",
    )

    assert previous_record is None


def test_same_invoice_is_detected_as_duplicate(tmp_path):
    repository = InvoiceRepository(tmp_path / "test.db")

    invoice, result = process_invoice(
        "INV-1001.pdf",
        repository,
    )

    assert result.status == ProcessingStatus.PROCESSED

    duplicate_invoice, duplicate_result = process_invoice(
        "INV-1001.pdf",
        repository,
    )

    assert duplicate_invoice.invoice_number == "INV-1001"
    assert duplicate_result.status == ProcessingStatus.DUPLICATE