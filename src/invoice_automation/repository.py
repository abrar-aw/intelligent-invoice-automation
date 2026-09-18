import sqlite3
from pathlib import Path

from dataclasses import dataclass
from datetime import datetime, UTC

from invoice_automation.models import Invoice, ProcessingStatus


class InvoiceRepository:
    """Persist invoice processing records in a SQLite database."""

    def __init__(self, database_path: Path):
        self.database_path = database_path
        self._initialize_database()

    def _initialize_database(self) -> None:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS processed_invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_number TEXT NOT NULL,
                    supplier_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    processed_at TEXT NOT NULL,
                    source_file TEXT NOT NULL
                )
                """
            )

    def save(
        self,
        invoice: Invoice,
        status: ProcessingStatus,
    ) -> None:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                INSERT INTO processed_invoices (
                    invoice_number,
                    supplier_id,
                    status,
                    processed_at,
                    source_file
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    invoice.invoice_number,
                    invoice.supplier_id,
                    status.value,
                    datetime.now(UTC).isoformat(),
                    invoice.source_file,
                ),
            )

    def find_by_invoice(
        self,
        supplier_id: str,
        invoice_number: str,
    ):
        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row

            row = connection.execute(
                """
                SELECT
                    invoice_number,
                    supplier_id,
                    status,
                    processed_at,
                    source_file
                FROM processed_invoices
                WHERE supplier_id = ?
                  AND invoice_number = ?
                LIMIT 1
                """,
                (supplier_id, invoice_number),
            ).fetchone()

        if row is None:
            return None

        return ProcessingRecord(
            invoice_number=row["invoice_number"],
            supplier_id=row["supplier_id"],
            status=ProcessingStatus(row["status"]),
            processed_at=datetime.fromisoformat(row["processed_at"]),
            source_file=row["source_file"],
        )


@dataclass(frozen=True)
class ProcessingRecord:
    """A record of a previously processed invoice."""

    invoice_number: str
    supplier_id: str
    status: ProcessingStatus
    processed_at: datetime
    source_file: str