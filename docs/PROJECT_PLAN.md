# Project Plan

## Definition of done

The final portfolio version should:

- Process invoices from a realistic input source.
- Extract structured invoice fields.
- Validate required fields and arithmetic consistency.
- Reconcile supplier, currency, PO existence, and PO amount.
- Detect duplicate invoice numbers.
- Route failures to an exception queue without losing the original document.
- Persist processing status and an audit trail in SQLite.
- Be safe to rerun without double-processing the same invoice.
- Produce an operational report and dashboard.
- Include automated tests for normal and failure paths.
- Have a documented UiPath orchestration option.
- Use only synthetic/demo data in the public repository.
