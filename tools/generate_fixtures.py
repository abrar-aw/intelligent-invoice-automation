from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle, Paragraph
from reportlab.lib import colors


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INCOMING_DIR = PROJECT_ROOT / "data" / "incoming"
REFERENCE_DIR = PROJECT_ROOT / "data" / "reference"


def create_invoice(
    file_name: str,
    invoice_number: str,
    supplier_id: str,
    supplier_name: str,
    invoice_date: str,
    due_date: str,
    po_number: str | None,
    currency: str,
    subtotal: str,
    tax: str,
    total: str,
) -> None:
    file_path = INCOMING_DIR / file_name

    document = SimpleDocTemplate(
        str(file_path),
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(
        Paragraph(
            f"<b>{supplier_name}</b><br/>"
            f"Supplier ID: {supplier_id}",
            styles["Normal"],
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph("<b>INVOICE</b>", styles["Title"])
    )

    elements.append(Spacer(1, 10))

    invoice_details = [
        ["Invoice Number", invoice_number],
        ["Invoice Date", invoice_date],
        ["Due Date", due_date],
        ["Purchase Order", po_number or ""],
        ["Currency", currency],
    ]

    details_table = Table(invoice_details, colWidths=[130, 300])

    details_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    elements.append(details_table)
    elements.append(Spacer(1, 20))

    items = [
        ["Description", "Qty", "Unit Price", "Amount"],
        ["Laptop Computers", "5", "$800.00", "$4,000.00"],
        ["USB-C Docking Stations", "10", "$120.00", "$1,200.00"],
    ]

    items_table = Table(
        items,
        colWidths=[220, 50, 90, 90],
    )

    items_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    elements.append(items_table)
    elements.append(Spacer(1, 20))

    totals = [
        ["Subtotal", subtotal],
        ["Tax", tax],
        ["Total", total],
    ]

    totals_table = Table(
        totals,
        colWidths=[360, 90],
        hAlign="RIGHT",
    )

    totals_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    elements.append(totals_table)

    document.build(elements)


def create_purchase_orders() -> None:
    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)

    purchase_orders = """po_number,supplier_id,currency,total,status
PO-5001,SUP-001,USD,5980.00,APPROVED
PO-5002,SUP-002,USD,2300.00,OPEN
PO-5003,SUP-003,USD,1150.00,CLOSED
PO-5004,SUP-001,USD,3450.00,APPROVED
"""

    (REFERENCE_DIR / "purchase_orders.csv").write_text(
        purchase_orders,
        encoding="utf-8",
    )


def main() -> None:
    INCOMING_DIR.mkdir(parents=True, exist_ok=True)

    create_purchase_orders()

    create_invoice(
        file_name="INV-1001.pdf",
        invoice_number="INV-1001",
        supplier_id="SUP-001",
        supplier_name="ABC Supplies Ltd.",
        invoice_date="18/09/2026",
        due_date="18/10/2026",
        po_number="PO-5001",
        currency="USD",
        subtotal="5200.00",
        tax="780.00",
        total="5980.00",
    )

    create_invoice(
        file_name="INV-1002.pdf",
        invoice_number="INV-1002",
        supplier_id="SUP-002",
        supplier_name="Global Office Solutions",
        invoice_date="18/09/2026",
        due_date="18/10/2026",
        po_number="PO-5002",
        currency="USD",
        subtotal="2000.00",
        tax="300.00",
        total="2300.00",
    )

    create_invoice(
        file_name="INV-1003.pdf",
        invoice_number="INV-1003",
        supplier_id="SUP-003",
        supplier_name="Tech Components Inc.",
        invoice_date="18/09/2026",
        due_date="18/10/2026",
        po_number="PO-5003",
        currency="USD",
        subtotal="1000.00",
        tax="150.00",
        total="1200.00",
    )

    create_invoice(
        file_name="INV-1004.pdf",
        invoice_number="INV-1004",
        supplier_id="SUP-001",
        supplier_name="ABC Supplies Ltd.",
        invoice_date="18/09/2026",
        due_date="18/10/2026",
        po_number=None,
        currency="USD",
        subtotal="3000.00",
        tax="450.00",
        total="3450.00",
    )

    create_invoice(
        file_name="INV-1005.pdf",
        invoice_number="INV-1005",
        supplier_id="SUP-001",
        supplier_name="ABC Supplies Ltd.",
        invoice_date="18/09/2026",
        due_date="18/10/2026",
        po_number="PO-5004",
        currency="USD",
        subtotal="3000.00",
        tax="450.00",
        total="3450.00",
    )

    print("Invoice fixtures generated successfully.")
    print(f"Incoming directory: {INCOMING_DIR}")
    print(f"Reference directory: {REFERENCE_DIR}")


if __name__ == "__main__":
    main()