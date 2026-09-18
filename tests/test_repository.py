from datetime import date
from decimal import Decimal
from datetime import datetime

from invoice_automation.models import Invoice, ProcessingStatus
from invoice_automation.repository import InvoiceRepository


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


def test_repository_starts_empty(tmp_path):
    repository = InvoiceRepository(tmp_path / "test.db")

    assert repository.find_by_invoice(
        "SUP-001",
        "INV-1001",
    ) is None


def test_repository_can_save_invoice(tmp_path):
    repository = InvoiceRepository(tmp_path / "test.db")
    invoice = make_invoice()

    repository.save(
        invoice,
        ProcessingStatus.PROCESSED,
    )

    record = repository.find_by_invoice(
        "SUP-001",
        "INV-1001",
    )

    assert record is not None
    assert record.invoice_number == "INV-1001"
    assert record.supplier_id == "SUP-001"
    assert record.status == ProcessingStatus.PROCESSED
    assert isinstance(record.processed_at, datetime)


def test_repository_can_distinguish_suppliers(tmp_path):
    repository = InvoiceRepository(tmp_path / "test.db")

    repository.save(
        make_invoice(supplier_id="SUP-001"),
        ProcessingStatus.PROCESSED,
    )

    assert repository.find_by_invoice(
        "SUP-001",
        "INV-1001",
    ) is not None

    assert repository.find_by_invoice(
        "SUP-002",
        "INV-1001",
    ) is None


def test_repository_persists_data(tmp_path):
    database_path = tmp_path / "test.db"

    repository = InvoiceRepository(database_path)

    repository.save(
        make_invoice(),
        ProcessingStatus.PROCESSED,
    )

    # Create a new repository instance using the same database.
    new_repository = InvoiceRepository(database_path)

    record = new_repository.find_by_invoice(
        "SUP-001",
        "INV-1001",
    )

    assert record is not None
    assert record.invoice_number == "INV-1001"