"""
seed_db.py – Populate the RNSIT Academic Data Engine Database
=============================================================
Creates a realistic, shareable database with:
  - 5 CSE students (3rd Semester, 2024-25 scheme)
  - All subject types: PCC, IPCC, PCCL, ESC, AEC, MC, UHV
  - Complete CIE (all components) and SEE marks for all subjects

Run once:
    python seed_db.py

The generated academic.db can be opened with any SQLite viewer
(DB Browser for SQLite, DBeaver, etc.) and shared with team members.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, engine, Base
import models
from services.cie_calculator import compute_cie, is_detained

Base.metadata.create_all(bind=engine)

# ─────────────────────────────────────────────────────────────────
#  RNSIT 2024 Scheme — III Semester CSE
#  Subject list with type info
# ─────────────────────────────────────────────────────────────────
SUBJECTS_3SEM = [
    # code,          name,                                             type,   credits
    ("BCS301",  "Discrete Mathematical Structures",                    "pcc",   3),
    ("BCS302",  "Analog and Digital Electronics",                      "pcc",   3),
    ("BCS303",  "Data Structures",                                     "pcc",   3),
    ("BCS304",  "Computer Organization and Architecture",              "ipcc",  4),
    ("BCSL305", "Data Structures Laboratory",                          "pccl",  1),
    ("BCS356A", "Biology for Engineers",                               "esc",   3),   # ESC Elective
    ("BCS357B", "Indian Constitution",                                 "aec",   2),   # AEC Elective
    ("BRMCK358","Management and Entrepreneurship",                     "mc",    0),   # Mandatory Course
    ("BUHK359", "Universal Human Values",                              "uhv",   1),   # UHV
]

# CIE component marks per student per subject
# PCC:   ia1(/50), ia2(/50), cce(/20)
# IPCC:  ia1(/50), ia2(/50), cce(/10), lab_rec(/12), lt1(/100), lt2(/100)
# PCCL:  lab_rec(/30), lt1(/100)
# ESC:   ia1(/50), ia2(/50), cce(/20)
# AEC:   ia1(/50), ia2(/50), cce(/20)
# MC:    direct(/100)
# UHV:   ia1(/50), ia2(/50), cce(/20)

STUDENTS = [
    {
        "name": "Bhargav Reddy", "usn": "1RN22CS001", "branch": "CSE",
        "marks": {
            "BCS301":  {"ia1": 42, "ia2": 46, "cce": 18},               # PCC
            "BCS302":  {"ia1": 38, "ia2": 40, "cce": 17},               # PCC
            "BCS303":  {"ia1": 44, "ia2": 45, "cce": 19},               # PCC
            "BCS304":  {"ia1": 40, "ia2": 42, "cce": 9, "lab_rec": 11, "lt1": 85, "lt2": 90},  # IPCC
            "BCSL305": {"lab_rec": 28, "lt1": 92},                       # PCCL
            "BCS356A": {"ia1": 43, "ia2": 47, "cce": 18},               # ESC
            "BCS357B": {"ia1": 40, "ia2": 42, "cce": 17},               # AEC
            "BRMCK358":{"direct": 72},                                   # MC
            "BUHK359": {"ia1": 40, "ia2": 44, "cce": 16},               # UHV
        },
        "see": {
            "BCS301": 80, "BCS302": 74, "BCS303": 88,
            "BCS304": 76, "BCSL305": 82,
            "BCS356A": 78, "BCS357B": 70, "BUHK359": 68,
        },
    },
    {
        "name": "Priya Sharma", "usn": "1RN22CS002", "branch": "CSE",
        "marks": {
            "BCS301":  {"ia1": 48, "ia2": 50, "cce": 20},
            "BCS302":  {"ia1": 44, "ia2": 46, "cce": 19},
            "BCS303":  {"ia1": 46, "ia2": 48, "cce": 20},
            "BCS304":  {"ia1": 45, "ia2": 47, "cce": 10, "lab_rec": 12, "lt1": 92, "lt2": 95},
            "BCSL305": {"lab_rec": 30, "lt1": 98},
            "BCS356A": {"ia1": 47, "ia2": 49, "cce": 20},
            "BCS357B": {"ia1": 46, "ia2": 48, "cce": 19},
            "BRMCK358":{"direct": 88},
            "BUHK359": {"ia1": 46, "ia2": 48, "cce": 19},
        },
        "see": {
            "BCS301": 92, "BCS302": 88, "BCS303": 94,
            "BCS304": 90, "BCSL305": 96,
            "BCS356A": 90, "BCS357B": 86, "BUHK359": 84,
        },
    },
    {
        "name": "Kiran Nair",  "usn": "1RN22CS003", "branch": "CSE",
        "marks": {
            "BCS301":  {"ia1": 34, "ia2": 36, "cce": 14},
            "BCS302":  {"ia1": 30, "ia2": 34, "cce": 13},
            "BCS303":  {"ia1": 36, "ia2": 38, "cce": 15},
            "BCS304":  {"ia1": 32, "ia2": 30, "cce": 7, "lab_rec": 9, "lt1": 70, "lt2": 65},
            "BCSL305": {"lab_rec": 22, "lt1": 74},
            "BCS356A": {"ia1": 35, "ia2": 37, "cce": 14},
            "BCS357B": {"ia1": 33, "ia2": 35, "cce": 14},
            "BRMCK358":{"direct": 62},
            "BUHK359": {"ia1": 35, "ia2": 37, "cce": 14},
        },
        "see": {
            "BCS301": 60, "BCS302": 56, "BCS303": 64,
            "BCS304": 58, "BCSL305": 70,
            "BCS356A": 62, "BCS357B": 54, "BUHK359": 58,
        },
    },
    {
        "name": "Ananya Bhat", "usn": "1RN22CS004", "branch": "CSE",
        "marks": {
            # Deliberately low CIE for BCS302 → show DETAINED scenario
            "BCS301":  {"ia1": 28, "ia2": 30, "cce": 12},
            "BCS302":  {"ia1": 14, "ia2": 16, "cce": 6},   # Will be detained (CIE < 20)
            "BCS303":  {"ia1": 32, "ia2": 34, "cce": 13},
            "BCS304":  {"ia1": 26, "ia2": 28, "cce": 6, "lab_rec": 8, "lt1": 60, "lt2": 55},
            "BCSL305": {"lab_rec": 18, "lt1": 62},
            "BCS356A": {"ia1": 28, "ia2": 30, "cce": 12},
            "BCS357B": {"ia1": 28, "ia2": 30, "cce": 12},
            "BRMCK358":{"direct": 58},
            "BUHK359": {"ia1": 28, "ia2": 30, "cce": 12},
        },
        "see": {
            "BCS301": 52, "BCS303": 56,
            "BCS304": 48, "BCSL305": 60,
            "BCS356A": 54, "BCS357B": 50, "BUHK359": 52,
            # BCS302 → detained, no SEE
        },
    },
    {
        "name": "Rohit Verma", "usn": "1RN22CS005", "branch": "CSE",
        "marks": {
            "BCS301":  {"ia1": 40, "ia2": 38, "cce": 16},
            "BCS302":  {"ia1": 36, "ia2": 34, "cce": 15},
            "BCS303":  {"ia1": 42, "ia2": 44, "cce": 17},
            "BCS304":  {"ia1": 38, "ia2": 40, "cce": 8, "lab_rec": 10, "lt1": 80, "lt2": 84},
            "BCSL305": {"lab_rec": 26, "lt1": 86},
            "BCS356A": {"ia1": 40, "ia2": 38, "cce": 16},
            "BCS357B": {"ia1": 38, "ia2": 40, "cce": 16},
            "BRMCK358":{"direct": 68},
            "BUHK359": {"ia1": 38, "ia2": 40, "cce": 15},
        },
        "see": {
            "BCS301": 72, "BCS302": 68, "BCS303": 78,
            "BCS304": 70, "BCSL305": 76,
            "BCS356A": 72, "BCS357B": 66, "BUHK359": 66,
        },
    },
]


def build_cie_payload(subj_type, marks):
    """Map flat marks dict to CIERecordCreate-compatible dict."""
    return {
        "ia_test1_raw":     marks.get("ia1"),
        "ia_test2_raw":     marks.get("ia2"),
        "cce_marks":        marks.get("cce"),
        "lab_record_marks": marks.get("lab_rec"),
        "lab_test1_raw":    marks.get("lt1"),
        "lab_test2_raw":    marks.get("lt2"),
        "direct_cie_marks": marks.get("direct"),
    }


def seed():
    db = SessionLocal()
    created_students = []

    print("\n" + "=" * 60)
    print("  RNSIT Academic Data Engine — Database Seeder")
    print("=" * 60)

    for sdata in STUDENTS:
        # ── Create student ──────────────────────────────────────
        existing = db.query(models.Student).filter(
            models.Student.usn == sdata["usn"]
        ).first()
        if existing:
            print(f"\n⚠  {sdata['usn']} already exists — skipping.")
            continue

        student = models.Student(
            name=sdata["name"],
            usn=sdata["usn"],
            branch=sdata["branch"],
            scheme="2024",
        )
        db.add(student)
        db.commit()
        db.refresh(student)
        print(f"\n✅ Student: {student.name} ({student.usn})")

        # ── Create semester ─────────────────────────────────────
        semester = models.Semester(
            student_id=student.id,
            semester_number=3,
            academic_year="2024-25",
        )
        db.add(semester)
        db.commit()
        db.refresh(semester)
        print(f"   Semester 3 (2024-25) created [ID {semester.id}]")

        # ── Create subjects + marks ─────────────────────────────
        for code, name, stype, credits in SUBJECTS_3SEM:
            subject = models.Subject(
                semester_id=semester.id,
                subject_code=code,
                subject_name=name,
                subject_type=models.SubjectType(stype),
                credits=credits,
                is_mandatory=(stype == "mc"),
                is_chosen=True,
            )
            db.add(subject)
            db.commit()
            db.refresh(subject)

            # CIE
            raw_marks = sdata["marks"].get(code, {})
            cie_payload = build_cie_payload(stype, raw_marks)
            computed = compute_cie(stype, cie_payload)
            detained = is_detained(computed.get("final_cie"), subject.is_mandatory)
            computed["is_detained"] = detained

            cie = models.CIERecord(subject_id=subject.id, **computed)
            db.add(cie)
            db.commit()

            # SEE (skip MC and detained subjects)
            see_raw = sdata["see"].get(code)
            if not subject.is_mandatory:
                reduced = round(see_raw / 2.0, 2) if see_raw and not detained else None
                see = models.SEEMark(
                    subject_id=subject.id,
                    raw_scored=see_raw if not detained else None,
                    reduced_scored=reduced,
                    is_absent=False,
                    is_detained=detained,
                )
                db.add(see)
                db.commit()

            # Status display
            cie_disp = f"CIE={computed['final_cie']}" if computed["final_cie"] is not None else "CIE=—"
            see_disp = "DETAINED" if detained else (f"SEE={see_raw}/100" if see_raw else "SEE=—" if not subject.is_mandatory else "MC(no SEE)")
            status = "🔴 DETAINED" if detained else "✅ OK" if see_raw else "⚠ CIE only"
            print(f"   [{stype.upper():5s}] {code:10s} | {cie_disp:13s} | {see_disp:15s} {status}")

        created_students.append(student)

    db.close()

    print("\n" + "=" * 60)
    print(f"  Seeding complete. {len(created_students)} students added.")
    print("=" * 60)
    print("\n📁 Database: academic.db  (share this file with your team)")
    print("🌐 Open app: http://localhost:8000")
    print("📖 API docs: http://localhost:8000/docs")
    print()


if __name__ == "__main__":
    seed()
