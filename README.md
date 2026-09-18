# Intelligent Invoice Processing & Reconciliation Automation

A portfolio-grade automation project that simulates a real accounts-payable workflow: ingest invoices, extract structured fields, validate business rules, reconcile against purchase orders, route exceptions, persist an audit trail, and generate operational reports.

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

## Development phases

1. Core domain model, validation, reconciliation, SQLite persistence, CLI.
2. PDF/text extraction and synthetic invoice dataset.
3. Exception queue, idempotency, reporting, and automated tests.
4. Email/API ingestion and notifications.
5. Streamlit operations dashboard.
6. UiPath orchestration layer.
7. End-to-end demo, documentation, screenshots, and CV-ready metrics.

## Quality standard

The project should be explainable line-by-line in an interview. We will avoid fake claims, hard-coded success metrics, copied workflows, or unnecessary dependencies. Metrics used on the CV will come from actual test/demo runs.
