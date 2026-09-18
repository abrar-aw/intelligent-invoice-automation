from dataclasses import dataclass

from invoice_automation.models import Invoice, PurchaseOrder, ValidationIssue


@dataclass(frozen=True)
class ReconciliationResult:
    """Result of matching an invoice against a purchase order."""

    matched: bool
    po_number: str | None
    issues: tuple[ValidationIssue, ...] = ()


def reconcile_invoice(
    invoice: Invoice,
    purchase_orders: list[PurchaseOrder],
) -> ReconciliationResult:
    """
    Reconcile an invoice against its referenced purchase order.

    All applicable reconciliation issues are collected rather than
    stopping at the first failure.
    """

    if not invoice.po_number:
        return ReconciliationResult(
            matched=False,
            po_number=None,
            issues=(
                ValidationIssue(
                    code="MISSING_PO",
                    message="Invoice does not contain a purchase order number.",
                ),
            ),
        )

    matching_po = next(
        (
            po
            for po in purchase_orders
            if po.po_number == invoice.po_number
        ),
        None,
    )

    if matching_po is None:
        return ReconciliationResult(
            matched=False,
            po_number=invoice.po_number,
            issues=(
                ValidationIssue(
                    code="PO_NOT_FOUND",
                    message=f"Purchase order '{invoice.po_number}' was not found.",
                ),
            ),
        )

    issues: list[ValidationIssue] = []

    if invoice.supplier_id != matching_po.supplier_id:
        issues.append(
            ValidationIssue(
                code="SUPPLIER_MISMATCH",
                message=(
                    f"Invoice supplier '{invoice.supplier_id}' does not match "
                    f"PO supplier '{matching_po.supplier_id}'."
                ),
            )
        )

    if invoice.currency != matching_po.currency:
        issues.append(
            ValidationIssue(
                code="CURRENCY_MISMATCH",
                message=(
                    f"Invoice currency '{invoice.currency}' does not match "
                    f"PO currency '{matching_po.currency}'."
                ),
            )
        )

    if invoice.total != matching_po.total:
        issues.append(
            ValidationIssue(
                code="PO_AMOUNT_MISMATCH",
                message=(
                    f"Invoice total '{invoice.total}' does not match "
                    f"PO total '{matching_po.total}'."
                ),
            )
        )

    if matching_po.status.upper() not in {"OPEN", "APPROVED"}:
        issues.append(
            ValidationIssue(
                code="PO_NOT_ACTIONABLE",
                message=(
                    f"Purchase order '{matching_po.po_number}' has "
                    f"non-actionable status '{matching_po.status}'."
                ),
            )
        )

    return ReconciliationResult(
        matched=not issues,
        po_number=matching_po.po_number,
        issues=tuple(issues),
    )