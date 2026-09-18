from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from invoice_automation.parser import InvoiceParseError, parse_invoice_text


def test_parse_complete_invoice():
    text = """
    Invoice Number: INV-1001
    Supplier ID: SUP-001
    Supplier: ABC Supplies Ltd.
    Invoice Date: 18/09/2026
    Due Date: 18/10/2026
    PO Number: PO-5001
    Currency: USD
    Subtotal: 5200.00
    Tax: 780.00
    Total: 5980.00
    """

    invoice = parse_invoice_text(text, "INV-1001.pdf")

    assert invoice.invoice_number == "INV-1001"
    assert invoice.supplier_id == "SUP-001"
    assert invoice.supplier_name == "ABC Supplies Ltd."
    assert invoice.invoice_date == date(2026, 9, 18)
    assert invoice.due_date == date(2026, 10, 18)
    assert invoice.po_number == "PO-5001"
    assert invoice.currency == "USD"
    assert invoice.subtotal == Decimal("5200.00")
    assert invoice.tax == Decimal("780.00")
    assert invoice.total == Decimal("5980.00")
    assert invoice.source_file == "INV-1001.pdf"


def test_parse_invoice_without_optional_fields():
    text = """
    Invoice Number: INV-1004
    Supplier ID: SUP-001
    Supplier: ABC Supplies Ltd.
    Invoice Date: 18/09/2026
    Due Date:
    PO Number:
    Currency: USD
    Subtotal: 3000.00
    Tax: 450.00
    Total: 3450.00
    """

    invoice = parse_invoice_text(text, "INV-1004.pdf")

    assert invoice.invoice_number == "INV-1004"
    assert invoice.due_date is None
    assert invoice.po_number is None
    assert invoice.total == Decimal("3450.00")


def test_parse_amounts_as_decimal():
    text = """
    Invoice Number: INV-1002
    Supplier ID: SUP-002
    Supplier: Global Office Solutions
    Invoice Date: 18/09/2026
    Due Date: 18/10/2026
    PO Number: PO-5002
    Currency: USD
    Subtotal: 2000.50
    Tax: 300.08
    Total: 2300.58
    """

    invoice = parse_invoice_text(text, "INV-1002.pdf")

    assert isinstance(invoice.subtotal, Decimal)
    assert isinstance(invoice.tax, Decimal)
    assert isinstance(invoice.total, Decimal)


def test_parser_strips_extra_whitespace():
    text = """
    Invoice Number:   INV-1001
    Supplier ID: SUP-001
    Supplier:   ABC Supplies Ltd.
    Invoice Date: 18/09/2026
    Due Date: 18/10/2026
    PO Number: PO-5001
    Currency: USD
    Subtotal: 5200.00
    Tax: 780.00
    Total: 5980.00
    """

    invoice = parse_invoice_text(text, "INV-1001.pdf")

    assert invoice.invoice_number == "INV-1001"
    assert invoice.supplier_name == "ABC Supplies Ltd."


def test_missing_required_field_raises_parse_error():
    text = """
    Supplier ID: SUP-001
    Supplier: ABC Supplies Ltd.
    Invoice Date: 18/09/2026
    Currency: USD
    Subtotal: 5200.00
    Tax: 780.00
    Total: 5980.00
    """

    with pytest.raises(InvoiceParseError):
        parse_invoice_text(text, "invalid.pdf")


def test_invalid_date_raises_parse_error():
    text = """
    Invoice Number: INV-1001
    Supplier ID: SUP-001
    Supplier: ABC Supplies Ltd.
    Invoice Date: not-a-date
    Due Date: 18/10/2026
    PO Number: PO-5001
    Currency: USD
    Subtotal: 5200.00
    Tax: 780.00
    Total: 5980.00
    """

    with pytest.raises(InvoiceParseError):
        parse_invoice_text(text, "invalid.pdf")


def test_invalid_amount_raises_parse_error():
    text = """
    Invoice Number: INV-1001
    Supplier ID: SUP-001
    Supplier: ABC Supplies Ltd.
    Invoice Date: 18/09/2026
    Due Date: 18/10/2026
    PO Number: PO-5001
    Currency: USD
    Subtotal: not-a-number
    Tax: 780.00
    Total: 5980.00
    """

    with pytest.raises(InvoiceParseError):
        parse_invoice_text(text, "invalid.pdf")


def test_parse_label_and_value_on_separate_lines():
    text = """
    Invoice Number
    INV-1001
    Supplier ID
    SUP-001
    Supplier
    ABC Supplies Ltd.
    Invoice Date
    18/09/2026
    Due Date
    18/10/2026
    PO Number
    PO-5001
    Currency
    USD
    Subtotal
    5200.00
    Tax
    780.00
    Total
    5980.00
    """

    invoice = parse_invoice_text(text, "INV-1001.pdf")

    assert invoice.invoice_number == "INV-1001"
    assert invoice.supplier_id == "SUP-001"
    assert invoice.supplier_name == "ABC Supplies Ltd."
    assert invoice.po_number == "PO-5001"
    assert invoice.total == Decimal("5980.00")


def test_optional_field_without_value_is_none():
    text = """
    Invoice Number
    INV-1004
    Supplier ID
    SUP-001
    Supplier
    ABC Supplies Ltd.
    Invoice Date
    18/09/2026
    Due Date
    18/10/2026
    PO Number
    Currency
    USD
    Subtotal
    3000.00
    Tax
    450.00
    Total
    3450.00
    """

    invoice = parse_invoice_text(text, "INV-1004.pdf")

    assert invoice.po_number is None
    assert invoice.currency == "USD"

def test_parse_supplier_name_from_first_line():
    text = """
    ABC Supplies Ltd.
    Supplier ID: SUP-001
    INVOICE
    Invoice Number
    INV-1001
    Invoice Date
    18/09/2026
    Due Date
    18/10/2026
    PO Number
    PO-5001
    Currency
    USD
    Subtotal
    5200.00
    Tax
    780.00
    Total
    5980.00
    """

    invoice = parse_invoice_text(text, "INV-1001.pdf")

    assert invoice.supplier_name == "ABC Supplies Ltd."


def test_parse_purchase_order_alias():
    text = """
    ABC Supplies Ltd.
    Supplier ID: SUP-001
    INVOICE
    Invoice Number
    INV-1001
    Invoice Date
    18/09/2026
    Due Date
    18/10/2026
    Purchase Order
    PO-5001
    Currency
    USD
    Subtotal
    5200.00
    Tax
    780.00
    Total
    5980.00
    """

    invoice = parse_invoice_text(text, "INV-1001.pdf")

    assert invoice.po_number == "PO-5001"