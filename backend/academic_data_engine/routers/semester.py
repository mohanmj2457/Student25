"""
routers/semester.py – Semester management (student-specific)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

router = APIRouter(tags=["Semesters"])


@router.post("/students/{student_id}/semesters/", response_model=schemas.SemesterOut, status_code=201)
def create_semester(student_id: int, payload: schemas.SemesterCreate, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    existing = db.query(models.Semester).filter(
        models.Semester.student_id == student_id,
        models.Semester.semester_number == payload.semester_number,
    ).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Semester {payload.semester_number} already exists for this student."
        )

    semester = models.Semester(student_id=student_id, **payload.model_dump())
    db.add(semester)
    db.commit()
    db.refresh(semester)
    return semester


@router.get("/students/{student_id}/semesters/", response_model=list[schemas.SemesterOut])
def list_semesters(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return db.query(models.Semester).filter(models.Semester.student_id == student_id).all()


@router.get("/semesters/{semester_id}", response_model=schemas.SemesterOut)
def get_semester(semester_id: int, db: Session = Depends(get_db)):
    sem = db.query(models.Semester).filter(models.Semester.id == semester_id).first()
    if not sem:
        raise HTTPException(status_code=404, detail="Semester not found")
    return sem


@router.delete("/students/{student_id}/semesters/{semester_id}", status_code=204)
def delete_semester(student_id: int, semester_id: int, db: Session = Depends(get_db)):
    sem = db.query(models.Semester).filter(
        models.Semester.id == semester_id,
        models.Semester.student_id == student_id,
    ).first()
    if not sem:
        raise HTTPException(status_code=404, detail="Semester not found for this student")
    db.delete(sem)
    db.commit()
