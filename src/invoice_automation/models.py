from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal
from enum import Enum


class ProcessingStatus(str, Enum):
    PROCESSED = "PROCESSED"
    EXCEPTION = "EXCEPTION"
    DUPLICATE = "DUPLICATE"


@dataclass(frozen=True)
class Invoice:
    invoice_number: str
    supplier_id: str
    supplier_name: str
    invoice_date: date
    due_date: date | None
    po_number: str | None
    currency: str
    subtotal: Decimal
    tax: Decimal
    total: Decimal
    source_file: str


@dataclass(frozen=True)
class PurchaseOrder:
    po_number: str
    supplier_id: str
    currency: str
    total: Decimal
    status: str = "OPEN"


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    severity: str = "ERROR"


@dataclass(frozen=True)
class ProcessingResult:
    invoice_number: str
    status: ProcessingStatus
    issues: tuple[ValidationIssue, ...] = ()
    processed_at: datetime = field(
    default_factory=lambda: datetime.now(UTC)
)