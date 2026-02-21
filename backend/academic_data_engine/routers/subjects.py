"""
routers/subjects.py – Subject CRUD (manual entry + update after PDF upload)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

router = APIRouter(tags=["Subjects"])


@router.post("/semesters/{semester_id}/subjects/", response_model=schemas.SubjectOut, status_code=201)
def create_subject(semester_id: int, payload: schemas.SubjectCreate, db: Session = Depends(get_db)):
    sem = db.query(models.Semester).filter(models.Semester.id == semester_id).first()
    if not sem:
        raise HTTPException(status_code=404, detail="Semester not found")

    # Check duplicate
    dup = db.query(models.Subject).filter(
        models.Subject.semester_id == semester_id,
        models.Subject.subject_code == payload.subject_code.strip().upper()
    ).first()
    if dup:
        raise HTTPException(status_code=409, detail=f"Subject {payload.subject_code} already exists in this semester")

    data = payload.model_dump()
    data["subject_code"] = data["subject_code"].strip().upper()
    # Set is_mandatory from type
    if data["subject_type"] == "mc":
        data["is_mandatory"] = True

    subject = models.Subject(semester_id=semester_id, **data)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


@router.get("/semesters/{semester_id}/subjects/", response_model=list[schemas.SubjectOut])
def list_subjects(semester_id: int, db: Session = Depends(get_db)):
    sem = db.query(models.Semester).filter(models.Semester.id == semester_id).first()
    if not sem:
        raise HTTPException(status_code=404, detail="Semester not found")
    return db.query(models.Subject).filter(models.Subject.semester_id == semester_id).all()


@router.get("/subjects/{subject_id}", response_model=schemas.SubjectOut)
def get_subject(subject_id: int, db: Session = Depends(get_db)):
    subj = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not subj:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subj


@router.put("/subjects/{subject_id}", response_model=schemas.SubjectOut)
def update_subject(subject_id: int, payload: schemas.SubjectUpdate, db: Session = Depends(get_db)):
    subj = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not subj:
        raise HTTPException(status_code=404, detail="Subject not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(subj, field, value)
    if subj.subject_type and subj.subject_type.value == "mc":
        subj.is_mandatory = True
    db.commit()
    db.refresh(subj)
    return subj


@router.delete("/subjects/{subject_id}", status_code=204)
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    subj = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not subj:
        raise HTTPException(status_code=404, detail="Subject not found")
    db.delete(subj)
    db.commit()
