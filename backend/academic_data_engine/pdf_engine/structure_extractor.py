"""
pdf_engine/structure_extractor.py – RNSIT 2024 Scheme Subject Extractor (v4)

Strategies:
  1. pdfplumber table extraction (best for bordered tables)
  2. pdfplumber text-line regex (fallback for plain-text PDFs)
  3. PyMuPDF text extraction (last resort)

For RNSIT, subject_type is inferred from the course code pattern:
  - Codes ending in L  (e.g. BCSL305) → pccl
  - Contains 'UHV' or 'BUHK' → uhv
  - Contains 'BRMCK' or 'MC' category → mc
  - Otherwise → pcc (default; user can refine after upload)
"""
import re
import logging
from typing import List, Dict, Optional, Tuple
from pdf_engine.pdf_reader import open_with_pdfplumber, open_with_pymupdf

logger = logging.getLogger(__name__)

# ── Column header keywords ─────────────────────────────────────────
HDR = {
    "code":    ["course code", "sub code", "subject code", "code", "sl.no", "sl no", "course\ncode"],
    "name":    ["course title", "subject title", "subject name", "subject", "title", "name", "course\ntitle"],
    "credits": ["credit", "cr ", "credits"],
    "cie":     ["cie", " ia ", "internal assessment", "internal marks"],
    "see":     ["see", " ee ", "external", "semester end", "end exam"],
    "ltp":     ["l-t-p", "l t p", "ltp", "hrs", "hours", "l:t:p", "l\nt\np"],
    "type":    ["category", "type", "subject type"],
}


def _match(cell: str, key: str) -> bool:
    if not cell:
        return False
    cl = " " + cell.lower().strip() + " "
    return any(kw in cl for kw in HDR[key])


def _clean(v) -> str:
    return re.sub(r"\s+", " ", str(v or "")).strip()


def _to_float(v) -> Optional[float]:
    try:
        return float(re.sub(r"[^\d.]", "", str(v or "")))
    except Exception:
        return None


def _infer_subject_type(code: str, name: str = "", type_hint: str = "") -> str:
    """
    Infer RNSIT subject type from course code pattern and name hints.
    Priority: explicit type column > code pattern > name keywords
    """
    c = code.upper().strip()
    h = type_hint.upper().strip()
    n = name.upper()

    # Explicit type hint from PDF column
    if h:
        if "IPCC" in h: return "ipcc"
        if "PCCL" in h or "LAB" in h: return "pccl"
        if "MC" in h or "MANDATORY" in h: return "mc"
        if "ESC" in h: return "esc"
        if "AEC" in h: return "aec"
        if "UHV" in h: return "uhv"
        if "PCC" in h: return "pcc"

    # RNSIT code patterns
    if re.match(r"B.{2,4}K\d{3}$", c) or "RMCK" in c:
        return "mc"   # Mandatory Course e.g. BRMCK357
    if "UHV" in c or "HVE" in c:
        return "uhv"
    # Codes ending in L are labs
    if re.match(r"[A-Z]{2,5}L\d{3}[A-Z]?$", c):
        return "pccl"
    # Name hints
    if "LAB" in n or "LABORATORY" in n or "PRACTICAL" in n:
        return "pccl"
    if "WORKSHOP" in n:
        return "pccl"
    # Default: PCC (theory)
    return "pcc"


def _detect_col_map(rows: List[List]) -> Optional[Dict[str, int]]:
    """Find header row and return {field: col_index}."""
    for row in rows[:15]:
        cells = [_clean(c) for c in (row or [])]
        m = {}
        for i, c in enumerate(cells):
            for key in HDR:
                if key not in m and _match(c, key):
                    m[key] = i
        if {"code", "name"}.issubset(m):
            return m
    return None


# ── Strategy 1: pdfplumber table extraction ───────────────────────

def _extract_via_tables(pdf_bytes: bytes) -> Tuple[List[Dict], List[str]]:
    warnings: List[str] = []
    subjects: List[Dict] = []

    doc = open_with_pdfplumber(pdf_bytes)
    if not doc:
        return subjects, ["pdfplumber could not open the PDF"]

    with doc as pdf:
        for pg_num, page in enumerate(pdf.pages):
            for table in (page.extract_tables() or []):
                if not table:
                    continue
                col_map = _detect_col_map(table)
                if not col_map:
                    continue

                hdr_idx = 0
                for i, row in enumerate(table[:15]):
                    if row and col_map.get("code") is not None:
                        cell = _clean(row[col_map["code"]])
                        if _match(cell, "code"):
                            hdr_idx = i
                            break

                for row in table[hdr_idx + 1:]:
                    if not row or all(not _clean(c) for c in row):
                        continue

                    code = _clean(row[col_map["code"]]) if "code" in col_map and col_map["code"] < len(row) else ""
                    name = _clean(row[col_map["name"]]) if "name" in col_map and col_map["name"] < len(row) else ""

                    if not code or not name:
                        continue
                    # Skip header-like rows
                    if re.fullmatch(r"[A-Za-z\s/()\-,.]+", code) and len(code) > 15:
                        continue
                    # Must look like a subject code
                    if not re.search(r"\d{2,}", code):
                        continue

                    def gf(k):
                        idx = col_map.get(k)
                        return _to_float(row[idx]) if idx is not None and idx < len(row) else None

                    type_hint = _clean(row[col_map["type"]]) if "type" in col_map and col_map["type"] < len(row) else ""
                    ltp = _clean(row[col_map["ltp"]]) if "ltp" in col_map and col_map["ltp"] < len(row) else None
                    credits = gf("credits") or 0.0
                    stype = _infer_subject_type(code, name, type_hint)

                    subjects.append({
                        "subject_code": code,
                        "subject_name": name,
                        "subject_type": stype,
                        "credits": credits,
                        "ltp_hours": ltp or None,
                        "is_mandatory": stype == "mc",
                    })

                if subjects:
                    logger.info(f"[table-strategy] Extracted {len(subjects)} subjects from page {pg_num + 1}")
                    return subjects, warnings

    return subjects, warnings


# ── Strategy 2: regex text-line parsing ──────────────────────────
# Matches lines like: BCS301   Data Structures   4   3-0-2
_ROW_PATTERN = re.compile(
    r"""
    ([A-Z]{2,5}L?\d{2,3}[A-Z0-9]{0,5})  # subject code
    \s{2,}
    (.+?)                                  # subject name (lazy)
    \s{2,}
    (\d+(?:\.\d+)?)                        # credits
    """,
    re.VERBOSE,
)


def _extract_via_text(pdf_bytes: bytes) -> Tuple[List[Dict], List[str]]:
    warnings: List[str] = []
    subjects: List[Dict] = []

    doc = open_with_pdfplumber(pdf_bytes)
    lines = []
    if doc:
        with doc as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                lines.extend(text.splitlines())
    else:
        fitz_doc = open_with_pymupdf(pdf_bytes)
        if fitz_doc:
            for page in fitz_doc:
                lines.extend(page.get_text().splitlines())
            fitz_doc.close()

    for line in lines:
        line = line.strip()
        m = _ROW_PATTERN.match(line)
        if not m:
            continue
        code = m.group(1)
        name = m.group(2).strip()
        credits_s = m.group(3)
        if len(name) < 4 or len(name) > 120:
            continue
        stype = _infer_subject_type(code, name)
        subjects.append({
            "subject_code": code,
            "subject_name": name,
            "subject_type": stype,
            "credits": float(credits_s),
            "ltp_hours": None,
            "is_mandatory": stype == "mc",
        })

    if subjects:
        logger.info(f"[text-strategy] Extracted {len(subjects)} subjects")
    else:
        warnings.append("Text-line regex found no subjects.")
    return subjects, warnings


# ── Strategy 3: PyMuPDF blocks ────────────────────────────────────

def _extract_via_fitz_blocks(pdf_bytes: bytes) -> Tuple[List[Dict], List[str]]:
    warnings: List[str] = []
    subjects: List[Dict] = []
    fitz_doc = open_with_pymupdf(pdf_bytes)
    if not fitz_doc:
        return subjects, ["PyMuPDF could not open PDF"]
    try:
        all_text = "\n".join(page.get_text("text") for page in fitz_doc)
        for m in _ROW_PATTERN.finditer(all_text):
            code = m.group(1)
            name = m.group(2).strip()
            if len(name) < 4:
                continue
            stype = _infer_subject_type(code, name)
            subjects.append({
                "subject_code": code,
                "subject_name": name,
                "subject_type": stype,
                "credits": float(m.group(3)),
                "ltp_hours": None,
                "is_mandatory": stype == "mc",
            })
    finally:
        fitz_doc.close()

    if not subjects:
        warnings.append(
            "PyMuPDF could not extract subjects. "
            "PDF may be image-based or scanned — please use manual entry."
        )
    return subjects, warnings


# ── Public API ─────────────────────────────────────────────────────

def extract_subjects_from_pdf(file_bytes: bytes) -> Tuple[List[Dict], List[str]]:
    """
    Try 3 strategies in order. Returns (subjects, warnings).
    Each subject dict has: subject_code, subject_name, subject_type,
                           credits, ltp_hours, is_mandatory.
    """
    all_warnings: List[str] = []

    subjects, w = _extract_via_tables(file_bytes)
    all_warnings.extend(w)
    if subjects:
        return subjects, all_warnings

    all_warnings.append("Table extraction found nothing; trying text-line strategy.")
    subjects, w = _extract_via_text(file_bytes)
    all_warnings.extend(w)
    if subjects:
        return subjects, all_warnings

    all_warnings.append("Text-line strategy found nothing; trying PyMuPDF.")
    subjects, w = _extract_via_fitz_blocks(file_bytes)
    all_warnings.extend(w)
    return subjects, all_warnings
