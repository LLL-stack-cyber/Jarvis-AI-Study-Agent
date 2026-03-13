"""Utilities for loading and indexing user-uploaded documents."""

from __future__ import annotations

import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, List
from xml.etree import ElementTree
from zipfile import ZipFile

logger = logging.getLogger(__name__)

# In-memory index for quick retrieval. This can later be replaced by a DB/vector store.
DOCUMENT_INDEX: DefaultDict[str, List[str]] = defaultdict(list)


class DocumentLoaderError(Exception):
    """Raised when document loading fails."""


def _clean_text(text: str) -> str:
    """Normalize whitespace while preserving paragraph breaks."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _read_txt(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8", errors="ignore")


def _read_docx(file_path: Path) -> str:
    with ZipFile(file_path) as archive:
        document_xml = archive.read("word/document.xml")

    root = ElementTree.fromstring(document_xml)
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs = []

    for paragraph in root.findall(".//w:p", namespace):
        texts = [node.text for node in paragraph.findall(".//w:t", namespace) if node.text]
        paragraph_text = "".join(texts).strip()
        if paragraph_text:
            paragraphs.append(paragraph_text)

    return "\n\n".join(paragraphs)


def _read_pdf(file_path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - depends on optional dependency
        raise DocumentLoaderError(
            "PDF support requires the 'pypdf' package. Install with: pip install pypdf"
        ) from exc

    reader = PdfReader(str(file_path))
    page_text = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(page_text)


def load_document(file_path: str) -> str:
    """Load a PDF, DOCX, or TXT file and return cleaned text content."""
    path = Path(file_path)

    if not path.exists() or not path.is_file():
        raise DocumentLoaderError(f"File not found: {file_path}")

    extension = path.suffix.lower()
    logger.info("Loading uploaded file '%s' with extension '%s'", path.name, extension)

    readers = {
        ".txt": _read_txt,
        ".docx": _read_docx,
        ".pdf": _read_pdf,
    }

    if extension not in readers:
        raise DocumentLoaderError(
            f"Unsupported file type '{extension}'. Supported formats: PDF, DOCX, TXT"
        )

    try:
        raw_text = readers[extension](path)
    except DocumentLoaderError:
        raise
    except Exception as exc:
        raise DocumentLoaderError(f"Failed to read document '{path.name}': {exc}") from exc

    cleaned_text = _clean_text(raw_text)
    logger.info("Successfully loaded '%s' (%d characters after cleaning)", path.name, len(cleaned_text))
    return cleaned_text


def index_document(user_id: str, text_content: str) -> None:
    """Store text content by user for future retrieval/querying."""
    cleaned_text = _clean_text(text_content)
    DOCUMENT_INDEX[user_id].append(cleaned_text)
    logger.info(
        "Indexed document content for user '%s' (entries=%d, chars=%d)",
        user_id,
        len(DOCUMENT_INDEX[user_id]),
        len(cleaned_text),
    )
