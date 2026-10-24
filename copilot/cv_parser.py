from pathlib import Path

import pymupdf  # PyMuPDF


def read_pdf(path: Path) -> str:
    with pymupdf.open(path) as doc:
        return "\n".join(page.get_text() for page in doc).strip()


def read_cv(path: str) -> str:
    """Read a CV from .pdf, .txt or .md and return plain text."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"CV not found: {p}")
    suffix = p.suffix.lower()
    if suffix == ".pdf":
        text = read_pdf(p)
    elif suffix in {".txt", ".md"}:
        text = p.read_text(encoding="utf-8").strip()
    else:
        raise ValueError(f"Unsupported file type: {suffix}")
    if not text:
        raise ValueError("No text found. If the PDF is a scanned image, use a text-based PDF.")
    return text
