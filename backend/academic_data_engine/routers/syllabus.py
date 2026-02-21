"""
routers/syllabus.py – PDF syllabus upload
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from pdf_engine.structure_extractor import extract_subjects_from_pdf
from services.subject_service import create_subject_from_row, upsert_subject

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Syllabus"])

MAX_PDF_MB = 20


@router.post("/upload-syllabus/{semester_id}", response_model=schemas.SyllabusUploadResponse, status_code=201)
async def upload_syllabus(
    semester_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a syllabus PDF. Subjects are extracted and stored automatically.
    Subject type (PCC / IPCC / PCCL / MC …) is auto-detected from the course code pattern.
    The user can still correct types after upload via the subject edit endpoint.
    """
    sem = db.query(models.Semester).filter(models.Semester.id == semester_id).first()
    if not sem:
        raise HTTPException(status_code=404, detail="Semester not found")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_PDF_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"PDF exceeds {MAX_PDF_MB} MB limit.")

    logger.info(f"Processing syllabus '{file.filename}' for semester {semester_id}")

    extracted_rows, warnings = extract_subjects_from_pdf(file_bytes)

    if not extracted_rows:
        warnings.append(
            "No subjects could be extracted from this PDF. "
            "Please use manual entry or check that the PDF contains a proper subject table."
        )

    stored = 0
    for row in extracted_rows:
        try:
            subject_data = create_subject_from_row(row)
            if subject_data["credits"] <= 0 and not subject_data["is_mandatory"]:
                warnings.append(f"Skipped '{subject_data['subject_code']}' – credits = 0 (likely a header row).")
                continue
            upsert_subject(db, semester_id, subject_data)
            stored += 1
        except Exception as exc:
            warnings.append(f"Could not store '{row.get('subject_code', '?')}': {exc}")

    logger.info(f"Stored {stored}/{len(extracted_rows)} subjects for semester {semester_id}")

    return schemas.SyllabusUploadResponse(
        semester_id=semester_id,
        subjects_extracted=len(extracted_rows),
        subjects_stored=stored,
        warnings=warnings,
    )
