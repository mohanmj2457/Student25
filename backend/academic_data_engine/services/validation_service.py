"""
services/validation_service.py – Reusable validation helpers
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session
import models


def check_duplicate_subject(db: Session, semester_id: int, subject_code: str, exclude_id: int = None):
    """Raise 409 if subject_code already exists in the semester."""
    query = db.query(models.Subject).filter(
        models.Subject.semester_id == semester_id,
        models.Subject.subject_code == subject_code.strip().upper(),
    )
    if exclude_id:
        query = query.filter(models.Subject.id != exclude_id)
    if query.first():
        raise HTTPException(
            status_code=409,
            detail=f"Subject with code '{subject_code}' already exists in this semester."
        )


def validate_marks(cie_scored: float, see_scored: float, subject: models.Subject):
    """Raise 422 if scored marks exceed the defined maxima."""
    errors = []
    if cie_scored > subject.cie_max:
        errors.append(
            f"CIE scored ({cie_scored}) exceeds CIE max ({subject.cie_max}) for subject '{subject.subject_name}'."
        )
    if see_scored > subject.see_max:
        errors.append(
            f"SEE scored ({see_scored}) exceeds SEE max ({subject.see_max}) for subject '{subject.subject_name}'."
        )
    if errors:
        raise HTTPException(status_code=422, detail={"validation_errors": errors})
