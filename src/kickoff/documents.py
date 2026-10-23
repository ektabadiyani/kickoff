"""Load a contract or statement of work as plain text."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


def load_document(path: str | Path) -> str:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix in {".md", ".txt"}:
        text = path.read_text(encoding="utf-8")
    elif suffix == ".pdf":
        reader = PdfReader(path)
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n\n".join(f"[Page {i}]\n{page}" for i, page in enumerate(pages, start=1))
        if not text.strip() or sum(len(p) for p in pages) < 200:
            raise ValueError(f"{path} has little or no extractable text. Is it a scanned image? Run OCR first.")
    else:
        raise ValueError(f"Unsupported file type '{suffix}'. Use .md, .txt or .pdf (save Word documents as PDF).")
    if not text.strip():
        raise ValueError(f"{path} is empty")
    return text
