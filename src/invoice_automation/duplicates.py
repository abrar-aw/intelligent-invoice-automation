from invoice_automation.models import Invoice


def is_duplicate(
    invoice: Invoice,
    previous_invoices: list[Invoice],
) -> bool:
    """Return True when the invoice matches a previously processed invoice."""
    return any(
        previous.invoice_number == invoice.invoice_number
        and previous.supplier_id == invoice.supplier_id
        for previous in previous_invoices
    )