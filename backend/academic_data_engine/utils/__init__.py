"""
utils/__init__.py – Shared utility helpers
"""
from typing import Any, Dict


def format_json_response(student_obj, semesters_list) -> Dict[str, Any]:
    """
    Build the standardised full JSON response consumed by the analytics module.
    Keeps this function decoupled from FastAPI so it can be tested independently.
    """
    sem_data = []
    for sem in semesters_list:
        subjects_data = []
        for subj in sem.subjects:
            marks = subj.marks
            subjects_data.append({
                "subject_code": subj.subject_code,
                "subject_name": subj.subject_name,
                "credits": subj.credits,
                "cie_max": subj.cie_max,
                "see_max": subj.see_max,
                "total_max": subj.total_max,
                "ltp_hours": subj.ltp_hours,
                "cie_scored": marks.cie_scored if marks else None,
                "see_scored": marks.see_scored if marks else None,
                "total_scored": marks.total_scored if marks else None,
                "grade": marks.grade if marks else None,
            })
        sem_data.append({
            "semester_number": sem.semester_number,
            "academic_year": sem.academic_year,
            "subjects": subjects_data,
        })

    return {
        "student": {
            "id": student_obj.id,
            "name": student_obj.name,
            "usn": student_obj.usn,
            "branch": student_obj.branch,
            "scheme": student_obj.scheme,
        },
        "semesters": sem_data,
    }
