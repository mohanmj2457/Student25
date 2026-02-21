"""
schemas.py – Pydantic v2 schemas (RNSIT 2024 Scheme — CIE+SEE only)
"""
from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, field_validator, ConfigDict
from models import SubjectType


# ── Student ────────────────────────────────────────────────────────

class StudentCreate(BaseModel):
    name: str
    usn: str
    branch: str
    scheme: str

class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    usn: str
    branch: str
    scheme: str
    created_at: datetime


# ── Semester ────────────────────────────────────────────────────────

class SemesterCreate(BaseModel):
    semester_number: int
    academic_year: str

    @field_validator("semester_number")
    @classmethod
    def positive(cls, v):
        if v <= 0:
            raise ValueError("Must be positive")
        return v

class SemesterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: int
    semester_number: int
    academic_year: str
    created_at: datetime


# ── Subject ─────────────────────────────────────────────────────────

class SubjectCreate(BaseModel):
    subject_code: str
    subject_name: str
    subject_type: SubjectType = SubjectType.pcc
    credits: float = 0.0
    ltp_hours: Optional[str] = None
    is_mandatory: bool = False
    option_group: Optional[str] = None
    is_chosen: bool = True

class SubjectUpdate(BaseModel):
    subject_name: Optional[str] = None
    subject_type: Optional[SubjectType] = None
    credits: Optional[float] = None
    is_chosen: Optional[bool] = None
    option_group: Optional[str] = None

class SubjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    semester_id: int
    subject_code: str
    subject_name: str
    subject_type: SubjectType
    credits: float
    ltp_hours: Optional[str]
    is_mandatory: bool
    option_group: Optional[str]
    is_chosen: bool


# ── CIE Record ───────────────────────────────────────────────────────

class CIERecordCreate(BaseModel):
    """
    Submit raw component marks. Server auto-computes scaled values and final_cie.
    PCC/ESC/AEC/UHV: ia_test1_raw, ia_test2_raw (/50 each) + cce_marks (/20)
    IPCC:  ia_test1_raw, ia_test2_raw (/50) + cce_marks (/10) + lab_record_marks (/12) + lab_test1_raw, lab_test2_raw (/100)
    PCCL:  lab_record_marks (/30) + lab_test1_raw (/100)
    MC:    direct_cie_marks (/100)
    """
    ia_test1_raw:     Optional[float] = None
    ia_test2_raw:     Optional[float] = None
    cce_marks:        Optional[float] = None
    lab_record_marks: Optional[float] = None
    lab_test1_raw:    Optional[float] = None
    lab_test2_raw:    Optional[float] = None
    direct_cie_marks: Optional[float] = None

class CIERecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    subject_id: int
    ia_test1_raw:     Optional[float]
    ia_test2_raw:     Optional[float]
    ia_scaled:        Optional[float]
    cce_marks:        Optional[float]
    lab_record_marks: Optional[float]
    lab_test1_raw:    Optional[float]
    lab_test2_raw:    Optional[float]
    lab_test_scaled:  Optional[float]
    direct_cie_marks: Optional[float]
    final_cie:        Optional[float]
    is_detained:      bool


# ── SEE Mark ─────────────────────────────────────────────────────────

class SEEMarkCreate(BaseModel):
    raw_scored:  Optional[float] = None  # out of 100 as written in hall
    is_absent:   bool = False

class SEEMarkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    subject_id: int
    raw_scored:     Optional[float]
    reduced_scored: Optional[float]   # auto: raw / 2 → /50
    is_absent:      bool
    is_detained:    bool


# ── Summary per semester (simple CIE+SEE output) ─────────────────────

class SubjectMarksSummary(BaseModel):
    subject_id:   int
    subject_code: str
    subject_name: str
    subject_type: str
    credits:      float
    is_mandatory: bool
    # CIE components (raw)
    ia_test1_raw:     Optional[float]
    ia_test2_raw:     Optional[float]
    ia_scaled:        Optional[float]
    cce_marks:        Optional[float]
    lab_record_marks: Optional[float]
    lab_test1_raw:    Optional[float]
    lab_test2_raw:    Optional[float]
    lab_test_scaled:  Optional[float]
    direct_cie_marks: Optional[float]
    # Final computed marks
    final_cie:      Optional[float]   # /50  (or /100 for MC)
    is_detained:    bool
    # SEE
    see_raw:        Optional[float]   # /100
    see_reduced:    Optional[float]   # /50
    is_absent:      bool
    # Status
    status: str   # "Complete" / "CIE Only" / "Pending" / "Detained" / "Absent"

class SemesterMarksSummary(BaseModel):
    semester_id:     int
    semester_number: int
    academic_year:   str
    subjects: List[SubjectMarksSummary]


# ── Syllabus ─────────────────────────────────────────────────────────

class SyllabusModuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    subject_id: int
    module_number: int
    module_title: Optional[str]
    topics: Optional[str]
    learning_objectives: Optional[str]

class SyllabusUploadResponse(BaseModel):
    semester_id: int
    subjects_extracted: int
    subjects_stored: int
    warnings: List[str] = []


# ── Full JSON export ──────────────────────────────────────────────────

class StudentFull(BaseModel):
    student: StudentOut
    semesters: List[SemesterMarksSummary] = []
