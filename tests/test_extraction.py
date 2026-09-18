from pathlib import Path

import pytest

from invoice_automation.extraction import (
    ExtractionError,
    extract_text_from_pdf,
)


FIXTURE_DIR = Path("data/incoming")


def test_extract_text_from_invoice():
    text = extract_text_from_pdf(FIXTURE_DIR / "INV-1001.pdf")

    assert "INV-1001" in text
    assert "ABC Supplies Ltd." in text
    assert "PO-5001" in text
    assert "5980.00" in text


def test_extract_text_contains_invoice_fields():
    text = extract_text_from_pdf(FIXTURE_DIR / "INV-1002.pdf")

    assert "INV-1002" in text
    assert "SUP-002" in text
    assert "Global Office Solutions" in text
    assert "2300.00" in text


def test_missing_pdf_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf(FIXTURE_DIR / "does-not-exist.pdf")


def test_non_pdf_file_raises_value_error(tmp_path):
    file_path = tmp_path / "invoice.txt"
    file_path.write_text("not a PDF")

    with pytest.raises(ValueError):
        extract_text_from_pdf(file_path)


def test_empty_pdf_raises_extraction_error(tmp_path):
    import pymupdf

    pdf_path = tmp_path / "empty.pdf"

    document = pymupdf.open()
    document.new_page()
    document.save(pdf_path)
    document.close()

    with pytest.raises(ExtractionError):
        extract_text_from_pdf(pdf_path)