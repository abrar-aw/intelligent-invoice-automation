from pathlib import Path

import pytest

from invoice_automation.ingestion import (
    calculate_file_hash,
    ingest_file,
)


def test_ingest_pdf(tmp_path: Path):
    invoice = tmp_path / "invoice.pdf"
    invoice.write_bytes(b"sample invoice")

    result = ingest_file(invoice)

    assert result.file_name == "invoice.pdf"
    assert result.status == "RECEIVED"
    assert len(result.file_hash) == 64
    assert result.processing_id


def test_reject_unsupported_file(tmp_path: Path):
    text_file = tmp_path / "invoice.txt"
    text_file.write_text("sample invoice")

    with pytest.raises(ValueError, match="Unsupported file type"):
        ingest_file(text_file)


def test_reject_missing_file(tmp_path: Path):
    missing_file = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError):
        ingest_file(missing_file)


def test_same_file_produces_same_hash(tmp_path: Path):
    invoice = tmp_path / "invoice.pdf"
    invoice.write_bytes(b"same invoice content")

    hash_one = calculate_file_hash(invoice)
    hash_two = calculate_file_hash(invoice)

    assert hash_one == hash_two

def test_discover_invoice_files(tmp_path: Path):
    from invoice_automation.ingestion import discover_invoice_files

    (tmp_path / "invoice_002.pdf").write_bytes(b"invoice 2")
    (tmp_path / "invoice_001.pdf").write_bytes(b"invoice 1")
    (tmp_path / "notes.txt").write_text("not an invoice")

    files = discover_invoice_files(tmp_path)

    assert [file.name for file in files] == [
        "invoice_001.pdf",
        "invoice_002.pdf",
    ]


def test_discover_invoice_files_missing_directory(tmp_path: Path):
    from invoice_automation.ingestion import discover_invoice_files

    missing_directory = tmp_path / "does_not_exist"

    with pytest.raises(FileNotFoundError):
        discover_invoice_files(missing_directory)


def test_discover_invoice_files_rejects_file(tmp_path: Path):
    from invoice_automation.ingestion import discover_invoice_files

    file_path = tmp_path / "invoice.pdf"
    file_path.write_bytes(b"invoice")

    with pytest.raises(ValueError, match="not a directory"):
        discover_invoice_files(file_path)