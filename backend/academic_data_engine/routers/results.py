"""
routers/results.py – Semester marks summary (CIE + SEE only, no grades/SGPA)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

router = APIRouter(tags=["Results"])


def _build_subject_summary(subj: models.Subject) -> schemas.SubjectMarksSummary:
    """Build a SubjectMarksSummary for one subject from DB."""
    cie = subj.cie_record
    see = subj.see_mark

    # Pull CIE components
    ia1      = cie.ia_test1_raw      if cie else None
    ia2      = cie.ia_test2_raw      if cie else None
    ia_sc    = cie.ia_scaled         if cie else None
    cce      = cie.cce_marks         if cie else None
    lab_rec  = cie.lab_record_marks  if cie else None
    lt1      = cie.lab_test1_raw     if cie else None
    lt2      = cie.lab_test2_raw     if cie else None
    lt_sc    = cie.lab_test_scaled   if cie else None
    direct   = cie.direct_cie_marks  if cie else None
    final_cie = cie.final_cie        if cie else None
    detained = cie.is_detained       if cie else False

    see_raw     = see.raw_scored     if see else None
    see_reduced = see.reduced_scored if see else None
    is_absent   = see.is_absent      if see else False

    # Status
    if detained:
        status = "Detained"
    elif is_absent:
        status = "Absent"
    elif final_cie is not None and (see_reduced is not None or subj.is_mandatory):
        status = "Complete"
    elif final_cie is not None:
        status = "CIE Only"
    else:
        status = "Pending"

    return schemas.SubjectMarksSummary(
        subject_id=subj.id,
        subject_code=subj.subject_code,
        subject_name=subj.subject_name,
        subject_type=subj.subject_type.value,
        credits=subj.credits,
        is_mandatory=subj.is_mandatory,
        ia_test1_raw=ia1,
        ia_test2_raw=ia2,
        ia_scaled=ia_sc,
        cce_marks=cce,
        lab_record_marks=lab_rec,
        lab_test1_raw=lt1,
        lab_test2_raw=lt2,
        lab_test_scaled=lt_sc,
        direct_cie_marks=direct,
        final_cie=final_cie,
        is_detained=detained,
        see_raw=see_raw,
        see_reduced=see_reduced,
        is_absent=is_absent,
        status=status,
    )


@router.get("/semesters/{semester_id}/marks-summary", response_model=schemas.SemesterMarksSummary)
def get_marks_summary(semester_id: int, db: Session = Depends(get_db)):
    """Return all CIE components, final CIE, and SEE marks for every subject in the semester."""
    sem = db.query(models.Semester).filter(models.Semester.id == semester_id).first()
    if not sem:
        raise HTTPException(404, "Semester not found")

    summaries = [_build_subject_summary(s) for s in sem.subjects if s.is_chosen]

    return schemas.SemesterMarksSummary(
        semester_id=sem.id,
        semester_number=sem.semester_number,
        academic_year=sem.academic_year,
        subjects=summaries,
    )
