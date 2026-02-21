"""
models.py – SQLAlchemy ORM models (RNSIT 2024 Scheme - Final Version)
CIE+SEE only, no SGPA/CGPA stored. Simplified Subject model (no cie_max/see_max - fixed by scheme type).
"""
from __future__ import annotations
import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    ForeignKey, UniqueConstraint, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from database import Base


class SubjectType(str, enum.Enum):
    pcc   = "pcc"    # Theory (3+ cr): IA avg→30/50 + CCE /20 = 50 CIE
    ipcc  = "ipcc"   # Theory+Lab (4 cr): IA→20 + CCE/10 + Lab Rec/12 + Lab Test→8 = 50 CIE
    pccl  = "pccl"   # Pure Lab (1 cr): Lab Rec/30 + Lab Test→20 = 50 CIE
    esc   = "esc"    # Elective Science (PCC-style CIE)
    aec   = "aec"    # Ability Enhancement (PCC-style CIE)
    mc    = "mc"     # Mandatory Course (0 cr, CIE /100 only, no SEE)
    uhv   = "uhv"    # Universal Human Values (PCC-style CIE)
    other = "other"  # Fallback (PCC-style CIE)


class Student(Base):
    __tablename__ = "students"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100), nullable=False)
    usn        = Column(String(20),  nullable=False, unique=True, index=True)
    branch     = Column(String(100), nullable=False)
    scheme     = Column(String(20),  nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    semesters = relationship("Semester", back_populates="student", cascade="all, delete-orphan")


class Semester(Base):
    __tablename__ = "semesters"

    id              = Column(Integer, primary_key=True, index=True)
    student_id      = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    semester_number = Column(Integer, nullable=False)
    academic_year   = Column(String(20), nullable=False)
    created_at      = Column(DateTime, default=datetime.utcnow)

    student  = relationship("Student", back_populates="semesters")
    subjects = relationship("Subject", back_populates="semester", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("student_id", "semester_number", name="uq_student_semester"),
    )


class Subject(Base):
    __tablename__ = "subjects"

    id           = Column(Integer, primary_key=True, index=True)
    semester_id  = Column(Integer, ForeignKey("semesters.id", ondelete="CASCADE"), nullable=False)
    subject_code = Column(String(20),  nullable=False)
    subject_name = Column(String(200), nullable=False)
    subject_type = Column(SAEnum(SubjectType), nullable=False, default=SubjectType.pcc)
    credits      = Column(Float, nullable=False, default=0.0)
    ltp_hours    = Column(String(20), nullable=True)
    is_mandatory = Column(Boolean, nullable=False, default=False)
    option_group = Column(String(30), nullable=True)
    is_chosen    = Column(Boolean, nullable=False, default=True)
    created_at   = Column(DateTime, default=datetime.utcnow)
    updated_at   = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    semester    = relationship("Semester", back_populates="subjects")
    cie_record  = relationship("CIERecord", back_populates="subject",
                               uselist=False, cascade="all, delete-orphan")
    see_mark    = relationship("SEEMark",   back_populates="subject",
                               uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("semester_id", "subject_code", name="uq_sem_subject"),
    )


class CIERecord(Base):
    """
    All CIE component marks + auto-computed scaled and final_cie.

    PCC/ESC/AEC/UHV/other (Theory):
        ia_test1_raw, ia_test2_raw  → each /50
        ia_scaled = avg * 30/50    → /30
        cce_marks                  → /20
        final_cie = ia_scaled + cce    → /50

    IPCC (Theory+Lab):
        ia_test1_raw, ia_test2_raw  → each /50
        ia_scaled = avg * 20/50    → /20
        cce_marks                  → /10
        lab_record_marks           → /12
        lab_test1_raw, lab_test2_raw → each /100
        lab_test_scaled = avg * 8/100 → /8
        final_cie = ia_sc + cce + lab_rec + lab_test_sc → /50

    PCCL (Pure Lab):
        lab_record_marks           → /30
        lab_test1_raw              → /100
        lab_test_scaled = lt1 * 20/100 → /20
        final_cie = lab_rec + lab_test_scaled → /50

    MC (Mandatory Course):
        direct_cie_marks           → /100
        final_cie = direct_cie_marks (out of 100)
    """
    __tablename__ = "cie_records"

    id               = Column(Integer, primary_key=True, index=True)
    subject_id       = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"),
                              nullable=False, unique=True)
    # IA Tests
    ia_test1_raw     = Column(Float, nullable=True)
    ia_test2_raw     = Column(Float, nullable=True)
    ia_scaled        = Column(Float, nullable=True)  # computed
    # CCE
    cce_marks        = Column(Float, nullable=True)
    # Lab
    lab_record_marks = Column(Float, nullable=True)
    lab_test1_raw    = Column(Float, nullable=True)
    lab_test2_raw    = Column(Float, nullable=True)
    lab_test_scaled  = Column(Float, nullable=True)  # computed
    # MC direct
    direct_cie_marks = Column(Float, nullable=True)
    # Computed total
    final_cie        = Column(Float, nullable=True)
    # Flag
    is_detained      = Column(Boolean, nullable=False, default=False)  # CIE /50 < 20

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    subject = relationship("Subject", back_populates="cie_record")


class SEEMark(Base):
    """SEE (Semester End Exam) — written /100, halved to /50."""
    __tablename__ = "see_marks"

    id             = Column(Integer, primary_key=True, index=True)
    subject_id     = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"),
                            nullable=False, unique=True)
    raw_scored     = Column(Float, nullable=True)   # /100 as written
    reduced_scored = Column(Float, nullable=True)   # /50  (= raw / 2)
    is_absent      = Column(Boolean, nullable=False, default=False)
    is_detained    = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    subject = relationship("Subject", back_populates="see_mark")
