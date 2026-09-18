from pathlib import Path

import pymupdf


class ExtractionError(Exception):
    """Raised when invoice text cannot be extracted from a PDF."""


def extract_text_from_pdf(file_path: Path) -> str:
    """
    Extract machine-readable text from a PDF.

    Raises:
        FileNotFoundError: If the PDF does not exist.
        ValueError: If the path is not a PDF file.
        ExtractionError: If the PDF cannot be opened or contains no text.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    if file_path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file: {file_path}")

    try:
        document = pymupdf.open(file_path)
    except Exception as exc:
        raise ExtractionError(
            f"Unable to open PDF: {file_path}"
        ) from exc

    try:
        text = "\n".join(page.get_text() for page in document)
    finally:
        document.close()

    text = text.strip()

    if not text:
        raise ExtractionError(
            f"No machine-readable text found in PDF: {file_path}"
        )

    return text