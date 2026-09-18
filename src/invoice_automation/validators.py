from __future__ import annotations

from decimal import Decimal
from .models import Invoice, PurchaseOrder, ValidationIssue


def validate_invoice(invoice: Invoice) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    if not invoice.invoice_number.strip():
        issues.append(ValidationIssue("MISSING_INVOICE_NUMBER", "Invoice number is missing."))
    if not invoice.supplier_id.strip():
        issues.append(ValidationIssue("MISSING_SUPPLIER", "Supplier ID is missing."))
    if invoice.subtotal < 0 or invoice.tax < 0 or invoice.total < 0:
        issues.append(ValidationIssue("NEGATIVE_AMOUNT", "Invoice amounts cannot be negative."))

    expected_total = invoice.subtotal + invoice.tax
    if abs(expected_total - invoice.total) > Decimal("0.01"):
        issues.append(
            ValidationIssue(
                "TOTAL_MISMATCH",
                f"Subtotal + tax ({expected_total}) does not equal total ({invoice.total}).",
            )
        )

    if invoice.due_date is not None and invoice.due_date < invoice.invoice_date:
        issues.append(ValidationIssue("INVALID_DUE_DATE", "Due date precedes invoice date."))

    if not invoice.currency.strip():
        issues.append(ValidationIssue("MISSING_CURRENCY", "Currency is missing."))

    return issues


def reconcile_with_po(invoice: Invoice, po: PurchaseOrder | None) -> list[ValidationIssue]:
    if not invoice.po_number:
        return [ValidationIssue("MISSING_PO", "Invoice does not contain a purchase-order number.")]
    if po is None:
        return [ValidationIssue("PO_NOT_FOUND", f"Purchase order {invoice.po_number} was not found.")]

    issues: list[ValidationIssue] = []
    if invoice.supplier_id != po.supplier_id:
        issues.append(ValidationIssue("SUPPLIER_MISMATCH", "Invoice supplier does not match the purchase order."))
    if invoice.currency != po.currency:
        issues.append(ValidationIssue("CURRENCY_MISMATCH", "Invoice currency does not match the purchase order."))
    if abs(invoice.total - po.total) > Decimal("0.01"):
        issues.append(
            ValidationIssue(
                "PO_AMOUNT_MISMATCH",
                f"Invoice total ({invoice.total}) does not match PO total ({po.total}).",
            )
        )
    if po.status.upper() not in {"OPEN", "APPROVED"}:
        issues.append(ValidationIssue("PO_NOT_ACTIONABLE", f"PO status is {po.status}.", "WARNING"))
    return issues
