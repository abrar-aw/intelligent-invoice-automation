# Intelligent Invoice Processing & Reconciliation Automation

A automation project that simulates a real accounts-payable workflow: ingest invoices, extract structured fields, validate business rules, reconcile against purchase orders, route exceptions, persist an audit trail, and generate operational reports.

## Project goals

- Automate repetitive invoice-processing work.
- Make business rules explicit and testable.
- Handle failures and exceptions without silently losing data.
- Keep an audit trail for every processing decision.
- Make the workflow idempotent so the same invoice is not processed twice.
- Use synthetic data only; no real financial or personal information.

## Planned architecture

```text
Incoming invoices
      |
      v
Document ingestion -> Extraction -> Validation -> Reconciliation
                                              |
                         +--------------------+--------------------+
                         |                    |                    |
                         v                    v                    v
                    Processed             Exceptions           Duplicates
                         |                    |                    |
                         +--------------------+--------------------+
                                              |
                                              v
                                    SQLite + Audit Log
                                              |
                                              v
                                      Reports / Dashboard
```

## Technology stack

- Python
- SQLite
- pandas
- PyMuPDF / OCR (later phase)
- pytest
- Streamlit (later phase)
- UiPath integration (later phase)

