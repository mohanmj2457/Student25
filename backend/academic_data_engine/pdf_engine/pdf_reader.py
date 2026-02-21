"""
pdf_engine/pdf_reader.py – PDF file loading utilities (v2)
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def open_with_pdfplumber(file_bytes: bytes):
    """Open PDF bytes with pdfplumber. Returns context-manager document or None."""
    try:
        import pdfplumber, io
        return pdfplumber.open(io.BytesIO(file_bytes))
    except Exception as e:
        logger.warning(f"pdfplumber open failed: {e}")
        return None


def open_with_pymupdf(file_bytes: bytes):
    """Open PDF bytes with PyMuPDF (fitz). Returns fitz.Document or None."""
    try:
        import fitz
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        return doc
    except Exception as e:
        logger.warning(f"PyMuPDF open failed: {e}")
        return None
