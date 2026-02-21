"""
routers/student.py – Student CRUD + full data export
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

router = APIRouter(tags=["Students"])


@router.post("/students/", response_model=schemas.StudentOut, status_code=201)
def create_student(payload: schemas.StudentCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Student).filter(
        models.Student.usn == payload.usn.strip().upper()
    ).first()
    if existing:
        raise HTTPException(409, f"Student with USN {payload.usn} already exists")
    student = models.Student(
        name=payload.name.strip(),
        usn=payload.usn.strip().upper(),
        branch=payload.branch.strip(),
        scheme=payload.scheme.strip(),
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.get("/students/", response_model=list[schemas.StudentOut])
def list_students(db: Session = Depends(get_db)):
    return db.query(models.Student).all()


@router.get("/students/{student_id}", response_model=schemas.StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)):
    s = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not s:
        raise HTTPException(404, "Student not found")
    return s


@router.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    s = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not s:
        raise HTTPException(404, "Student not found")
    db.delete(s)
    db.commit()
