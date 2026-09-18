from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from uuid import uuid4


SUPPORTED_EXTENSIONS = {".pdf"}


@dataclass
class IngestionResult:
    processing_id: str
    file_name: str
    file_path: Path
    file_hash: str
    status: str


def calculate_file_hash(file_path: Path) -> str:
    """Calculate the SHA-256 hash of a file."""
    hasher = sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def ingest_file(file_path: Path) -> IngestionResult:
    """Validate and register an invoice file for processing."""

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {file_path.suffix}"
        )

    file_hash = calculate_file_hash(file_path)

    return IngestionResult(
        processing_id=str(uuid4()),
        file_name=file_path.name,
        file_path=file_path,
        file_hash=file_hash,
        status="RECEIVED",
    )

def discover_invoice_files(directory: Path) -> list[Path]:
    """Discover supported invoice files in a directory."""

    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    if not directory.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")

    return sorted(
        file_path
        for file_path in directory.iterdir()
        if file_path.is_file()
        and file_path.suffix.lower() in SUPPORTED_EXTENSIONS
    )