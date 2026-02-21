"""
routers/marks.py – CIE and SEE marks entry (RNSIT 2024 Scheme)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from services.cie_calculator import compute_cie, is_detained

router = APIRouter(tags=["Marks"])


# ── CIE entry ─────────────────────────────────────────────────────

@router.post("/subjects/{subject_id}/cie", response_model=schemas.CIERecordOut, status_code=201)
def save_cie(subject_id: int, payload: schemas.CIERecordCreate, db: Session = Depends(get_db)):
    """Enter CIE component marks. Server auto-computes scaled values and final_cie."""
    subj = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not subj:
        raise HTTPException(404, "Subject not found")

    computed = compute_cie(subj.subject_type.value, payload.model_dump())
    computed["is_detained"] = is_detained(computed.get("final_cie"), subj.is_mandatory)

    rec = db.query(models.CIERecord).filter(models.CIERecord.subject_id == subject_id).first()
    if rec:
        for k, v in computed.items():
            setattr(rec, k, v)
    else:
        rec = models.CIERecord(subject_id=subject_id, **computed)
        db.add(rec)

    # Sync detained flag to SEE record if it exists
    see = db.query(models.SEEMark).filter(models.SEEMark.subject_id == subject_id).first()
    if see:
        see.is_detained = computed["is_detained"]

    db.commit()
    db.refresh(rec)
    return rec


@router.get("/subjects/{subject_id}/cie", response_model=schemas.CIERecordOut)
def get_cie(subject_id: int, db: Session = Depends(get_db)):
    rec = db.query(models.CIERecord).filter(models.CIERecord.subject_id == subject_id).first()
    if not rec:
        raise HTTPException(404, "CIE record not found")
    return rec


# ── SEE entry ─────────────────────────────────────────────────────

@router.post("/subjects/{subject_id}/see", response_model=schemas.SEEMarkOut, status_code=201)
def save_see(subject_id: int, payload: schemas.SEEMarkCreate, db: Session = Depends(get_db)):
    """Enter SEE raw marks (/100). Reduced score (/50) auto-computed."""
    subj = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not subj:
        raise HTTPException(404, "Subject not found")
    if subj.is_mandatory:
        raise HTTPException(400, "MC (Mandatory Course) subjects have no SEE")

    cie_rec = db.query(models.CIERecord).filter(models.CIERecord.subject_id == subject_id).first()
    detained = cie_rec.is_detained if cie_rec else False

    reduced = None
    if not payload.is_absent and payload.raw_scored is not None:
        reduced = round(payload.raw_scored / 2.0, 2)

    mark = db.query(models.SEEMark).filter(models.SEEMark.subject_id == subject_id).first()
    if mark:
        mark.raw_scored = payload.raw_scored
        mark.reduced_scored = reduced
        mark.is_absent = payload.is_absent
        mark.is_detained = detained
    else:
        mark = models.SEEMark(
            subject_id=subject_id,
            raw_scored=payload.raw_scored,
            reduced_scored=reduced,
            is_absent=payload.is_absent,
            is_detained=detained,
        )
        db.add(mark)

    db.commit()
    db.refresh(mark)
    return mark


@router.get("/subjects/{subject_id}/see", response_model=schemas.SEEMarkOut)
def get_see(subject_id: int, db: Session = Depends(get_db)):
    mark = db.query(models.SEEMark).filter(models.SEEMark.subject_id == subject_id).first()
    if not mark:
        raise HTTPException(404, "SEE mark not found")
    return mark
