"""
services/subject_service.py – Subject creation from PDF-extracted rows
"""
import re
from sqlalchemy.orm import Session
import models


def normalize_code(code: str) -> str:
    return re.sub(r"\s+", "", code).upper()


def create_subject_from_row(row_dict: dict) -> dict:
    """Convert a PDF-extracted row dict to a clean subject dict with subject_type."""
    def safe_float(val, default=0.0):
        try:
            return float(str(val or "").strip().replace(",", "."))
        except (TypeError, ValueError):
            return default

    stype = str(row_dict.get("subject_type", "pcc")).lower()
    valid_types = {"pcc", "ipcc", "pccl", "esc", "aec", "mc", "uhv", "other"}
    if stype not in valid_types:
        stype = "pcc"

    is_mandatory = (stype == "mc") or bool(row_dict.get("is_mandatory", False))

    return {
        "subject_code": normalize_code(str(row_dict.get("subject_code", "UNKNOWN"))),
        "subject_name": str(row_dict.get("subject_name", "Unknown Subject")).strip(),
        "subject_type": stype,
        "credits": safe_float(row_dict.get("credits", 0), 0.0),
        "ltp_hours": str(row_dict.get("ltp_hours", "")).strip() or None,
        "is_mandatory": is_mandatory,
        "option_group": row_dict.get("option_group"),
        "is_chosen": True,
    }


def upsert_subject(db: Session, semester_id: int, subject_data: dict) -> tuple:
    """Insert or update a subject. Returns (subject, created: bool)."""
    code = subject_data["subject_code"]
    existing = db.query(models.Subject).filter(
        models.Subject.semester_id == semester_id,
        models.Subject.subject_code == code,
    ).first()

    if existing:
        for field, val in subject_data.items():
            if hasattr(existing, field):
                setattr(existing, field, val)
        db.commit()
        db.refresh(existing)
        return existing, False

    subject = models.Subject(semester_id=semester_id, **subject_data)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject, True
