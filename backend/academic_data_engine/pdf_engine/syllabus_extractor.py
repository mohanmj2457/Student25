"""
pdf_engine/syllabus_extractor.py
Extracts per-subject module/topic content from detailed syllabus pages using PyMuPDF.
"""
import re
import logging
from typing import List, Dict, Tuple
from pdf_engine.pdf_reader import open_with_pymupdf

logger = logging.getLogger(__name__)

# Regex patterns
MODULE_PATTERN = re.compile(
    r"(?:Module|UNIT|Unit|MODULE)\s*[-–:]?\s*(\d+)\s*[:\-–]?\s*(.*?)(?=\n|$)",
    re.IGNORECASE,
)
COURSE_CODE_PATTERN = re.compile(r"\b([A-Z]{2,5}\d{2,6}[A-Z]?)\b")
OBJECTIVES_START = re.compile(
    r"(course\s+objective|learning\s+objective|objective)",
    re.IGNORECASE,
)
OBJECTIVES_END = re.compile(
    r"(module|unit|course\s+outcome|co\s*\d|references|text\s+book)",
    re.IGNORECASE,
)


def _find_subject_page(doc, subject_code: str) -> List[int]:
    """Return page indices where the subject code appears."""
    pages = []
    for i in range(len(doc)):
        text = doc[i].get_text()
        if subject_code.upper() in text.upper():
            pages.append(i)
    return pages


def _extract_modules(text: str) -> List[Dict]:
    """Parse module headers and their content from raw page text."""
    modules = []
    lines = text.splitlines()

    current_module = None
    current_title = ""
    current_topics: List[str] = []

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue

        mod_match = MODULE_PATTERN.match(line_stripped)
        if mod_match:
            # Save previous module
            if current_module is not None:
                modules.append({
                    "module_number": current_module,
                    "module_title": current_title.strip(),
                    "topics": "\n".join(current_topics).strip(),
                })
            current_module = int(mod_match.group(1))
            current_title = mod_match.group(2).strip()
            current_topics = []
        elif current_module is not None:
            # Skip lines that look like pagination/headers
            if len(line_stripped) > 2 and not re.match(r"^\d+$", line_stripped):
                current_topics.append(line_stripped)

    # Save last module
    if current_module is not None:
        modules.append({
            "module_number": current_module,
            "module_title": current_title.strip(),
            "topics": "\n".join(current_topics).strip(),
        })

    return modules


def _extract_learning_objectives(text: str) -> str:
    """Extract learning objectives block from text."""
    obj_lines: List[str] = []
    capturing = False

    for line in text.splitlines():
        stripped = line.strip()
        if OBJECTIVES_START.search(stripped):
            capturing = True
            continue
        if capturing:
            if OBJECTIVES_END.search(stripped) and obj_lines:
                break
            if stripped:
                obj_lines.append(stripped)

    return "\n".join(obj_lines[:20])  # cap at 20 lines


def extract_subject_syllabus(file_bytes: bytes, subject_code: str) -> Tuple[List[Dict], List[str]]:
    """
    Extract modules/topics for a specific subject from the full PDF.
    Returns (list_of_module_dicts, warnings).
    """
    warnings: List[str] = []
    results: List[Dict] = []

    doc = open_with_pymupdf(file_bytes)
    if doc is None:
        warnings.append("Could not open PDF with PyMuPDF.")
        return results, warnings

    pages = _find_subject_page(doc, subject_code)
    if not pages:
        warnings.append(f"Subject code '{subject_code}' not found in any page of the PDF.")
        doc.close()
        return results, warnings

    # Aggregate text from all matching pages (and the next page for continuation)
    full_text = ""
    visited = set()
    for p in pages:
        for pg in [p, p + 1]:
            if pg < len(doc) and pg not in visited:
                full_text += doc[pg].get_text() + "\n"
                visited.add(pg)

    doc.close()

    objectives = _extract_learning_objectives(full_text)
    modules = _extract_modules(full_text)

    if not modules:
        warnings.append(
            f"No module headings found for '{subject_code}'. "
            "PDF may not follow standard formatting."
        )

    for mod in modules:
        mod["learning_objectives"] = objectives if mod["module_number"] == 1 else ""

    return modules, warnings
