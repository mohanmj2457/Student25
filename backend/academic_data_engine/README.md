# RNSIT Academic Data Engine — Complete Technical Handoff

> **Purpose of this document:** Full technical context so any developer or AI assistant can understand, run, extend, or debug this system without any prior knowledge.

---

## 1. What We Built

A **web-based marks management system** for RNSIT students under the **2024 Autonomous Scheme**.

The core job: accept raw CIE component marks → auto-scale them per the scheme rules → accept SEE raw marks → halve them → store everything in a SQLite database → expose it all via a clean REST API and a browser wizard UI.

### What it does NOT do (intentionally simplified)
- No SGPA / CGPA calculation
- No grade letters (S, A, B …)
- No PDF syllabus content extraction (module-by-module)
- No authentication / login
- No cloud database (pure local SQLite)

---

## 2. RNSIT 2024 Scheme — CIE Rules (Critical Domain Knowledge)

This is the core business logic. Everything else in the codebase implements these rules.

### Subject Types

| Code | Full Name | Credits | CIE Structure | Has SEE? |
|------|-----------|---------|---------------|----------|
| PCC | Professional Core Course (Theory) | 3 | IA avg→30 + CCE→20 = **50** | ✅ |
| IPCC | Integrated Professional Core Course | 4 | IA avg→20 + CCE→10 + Lab Rec→12 + Lab Test avg→8 = **50** | ✅ |
| PCCL | Professional Core Course Lab | 1 | Lab Rec→30 + Lab Test→20 = **50** | ✅ |
| ESC | Emerging Science Course (elective) | 3 | Same as PCC | ✅ |
| AEC | Ability Enhancement Course (elective) | 2 | Same as PCC | ✅ |
| MC | Mandatory Course | 0 | Direct marks /100 | ❌ |
| UHV | Universal Human Values | 1 | Same as PCC | ✅ |
| other | Fallback | any | Same as PCC | ✅ |

### CIE Scaling Formulas (implemented in `services/cie_calculator.py`)

**PCC / ESC / AEC / UHV / other:**
```
ia_scaled = avg(ia_test1, ia_test2) × 30/50    → /30
final_cie = ia_scaled + cce_marks              → /50  (capped)
```

**IPCC:**
```
ia_scaled       = avg(ia_test1, ia_test2) × 20/50   → /20
lab_test_scaled = avg(lab_test1, lab_test2) × 8/100 → /8
final_cie       = ia_scaled + cce + lab_record + lab_test_scaled → /50
```

**PCCL:**
```
lab_test_scaled = lab_test1 × 20/100   → /20
final_cie       = lab_record + lab_test_scaled → /50
```

**MC:**
```
final_cie = direct_cie_marks    → /100  (not scaled)
```

### Detention Rule
```
If final_cie < 20 (out of 50) AND subject is not MC → student is DETAINED
Detained students cannot appear in SEE.
```

### SEE Conversion
```
SEE raw mark is written out of 100
reduced_scored = raw_scored / 2    → stored as /50
```

---

## 3. Project Structure

```
c:\SIC Hacakthon\academic_data_engine\
│
├── main.py                      # FastAPI app entry point
├── models.py                    # SQLAlchemy ORM (tables)
├── schemas.py                   # Pydantic v2 request/response models
├── database.py                  # SQLite connection + Base + get_db
├── requirements.txt             # Python dependencies
├── seed_db.py                   # One-time database seeder (5 students, full data)
├── academic.db                  # SQLite database file (share this)
├── README.md                    # This file
│
├── services/
│   ├── cie_calculator.py        # compute_cie(), is_detained() — core logic
│   └── subject_service.py       # create_subject_from_row(), upsert_subject()
│
├── routers/
│   ├── student.py               # POST/GET /students/
│   ├── semester.py              # POST/GET /students/{id}/semesters/
│   ├── subjects.py              # CRUD /semesters/{id}/subjects/
│   ├── syllabus.py              # POST /upload-syllabus/{sem_id}  ← PDF upload
│   ├── marks.py                 # POST /subjects/{id}/cie  and  /see
│   └── results.py               # GET  /semesters/{id}/marks-summary
│
├── pdf_engine/
│   ├── structure_extractor.py   # Extracts subject rows from PDF (3 strategies)
│   └── pdf_reader.py            # Opens PDF bytes with pdfplumber / PyMuPDF
│
└── frontend/
    ├── index.html               # 6-step wizard HTML
    ├── style.css                # Dark theme CSS
    └── app.js                   # All wizard logic (vanilla JS, no framework)
```

---

## 4. Database Schema (SQLite — `academic.db`)

### Tables

```sql
-- One row per student
students (
  id INTEGER PK,
  name TEXT,
  usn TEXT UNIQUE,    -- e.g. 1RN22CS001
  branch TEXT,        -- e.g. CSE
  scheme TEXT,        -- always "2024"
  created_at DATETIME,
  updated_at DATETIME
)

-- Many semesters per student
semesters (
  id INTEGER PK,
  student_id INTEGER FK → students.id,
  semester_number INTEGER,  -- 1–8
  academic_year TEXT,       -- e.g. "2024-25"
  created_at DATETIME,
  UNIQUE(student_id, semester_number)
)

-- Many subjects per semester
subjects (
  id INTEGER PK,
  semester_id INTEGER FK → semesters.id,
  subject_code TEXT,         -- e.g. BCS301
  subject_name TEXT,
  subject_type TEXT,         -- pcc|ipcc|pccl|esc|aec|mc|uhv|other
  credits REAL,
  ltp_hours TEXT,            -- e.g. "3-0-2" (optional)
  is_mandatory BOOLEAN,      -- TRUE for MC subjects
  option_group TEXT,         -- for elective buckets (optional)
  is_chosen BOOLEAN,         -- FALSE if student opted out of elective
  UNIQUE(semester_id, subject_code)
)

-- One CIE record per subject (all components stored raw + computed)
cie_records (
  id INTEGER PK,
  subject_id INTEGER FK → subjects.id UNIQUE,
  -- raw inputs
  ia_test1_raw REAL,         -- /50
  ia_test2_raw REAL,         -- /50
  cce_marks REAL,            -- /20 (PCC) or /10 (IPCC)
  lab_record_marks REAL,     -- /12 (IPCC) or /30 (PCCL)
  lab_test1_raw REAL,        -- /100
  lab_test2_raw REAL,        -- /100
  direct_cie_marks REAL,     -- /100 for MC
  -- auto-computed
  ia_scaled REAL,            -- computed by server
  lab_test_scaled REAL,      -- computed by server
  final_cie REAL,            -- THE key output: /50 (or /100 for MC)
  is_detained BOOLEAN,       -- final_cie < 20
  created_at DATETIME,
  updated_at DATETIME
)

-- One SEE record per subject (MC subjects have no SEE row)
see_marks (
  id INTEGER PK,
  subject_id INTEGER FK → subjects.id UNIQUE,
  raw_scored REAL,           -- as written in hall: /100
  reduced_scored REAL,       -- auto: raw/2 → /50
  is_absent BOOLEAN,
  is_detained BOOLEAN,       -- copied from CIE (detained = can't sit SEE)
  created_at DATETIME,
  updated_at DATETIME
)
```

### Relationships (cascade delete)
```
Student → Semesters → Subjects → CIERecord
                               → SEEMark
```

---

## 5. API Reference

**Base URL:** `http://localhost:8000`  
**Interactive docs:** `http://localhost:8000/docs`

### Students
```
POST   /students/              Create student     Body: {name, usn, branch, scheme}
GET    /students/              List all students
GET    /students/{id}          Get one student
DELETE /students/{id}          Delete student (cascades all data)
```

### Semesters
```
POST   /students/{id}/semesters/   Create semester    Body: {semester_number, academic_year}
GET    /students/{id}/semesters/   List semesters
GET    /semesters/{id}             Get one semester
DELETE /semesters/{id}             Delete semester
```

### Subjects
```
POST   /semesters/{id}/subjects/   Add subject manually
GET    /semesters/{id}/subjects/   List subjects in semester
GET    /subjects/{id}              Get one subject
PUT    /subjects/{id}              Update subject (type, credits, is_chosen, option_group)
DELETE /subjects/{id}              Delete subject
```

### PDF Upload (auto-extract subjects from syllabus)
```
POST   /upload-syllabus/{semester_id}
  multipart form: file=<.pdf>
  Response: { semester_id, subjects_extracted, subjects_stored, warnings[] }
```
PDF extraction tries 3 strategies in order:
1. pdfplumber table detection (best for bordered tables)
2. pdfplumber + regex text line parsing (fallback)
3. PyMuPDF block text + regex (last resort)

Subject type is auto-inferred from course code:
- Code ending in `L` + digits → `pccl`
- Code containing `RMCK` → `mc`
- Code containing `UHV`/`HVE` → `uhv`
- Otherwise → `pcc` (user can correct in Step 4 of UI)

### CIE Marks Entry
```
POST   /subjects/{id}/cie
Body (send whichever fields apply to the subject type):
{
  "ia_test1_raw": 42,       -- /50  (PCC, IPCC, ESC, AEC, UHV)
  "ia_test2_raw": 46,       -- /50
  "cce_marks": 18,          -- /20 PCC  or /10 IPCC
  "lab_record_marks": 11,   -- /12 IPCC or /30 PCCL
  "lab_test1_raw": 85,      -- /100 (IPCC, PCCL)
  "lab_test2_raw": 90,      -- /100 (IPCC only)
  "direct_cie_marks": 75    -- /100 (MC only)
}
Response: CIERecordOut  (includes ia_scaled, lab_test_scaled, final_cie, is_detained)

GET    /subjects/{id}/cie     Retrieve stored CIE record
```

### SEE Marks Entry
```
POST   /subjects/{id}/see
Body: { "raw_scored": 80, "is_absent": false }
Response: SEEMarkOut  (includes reduced_scored = raw/2)
NOTE: MC subjects will return 400 (no SEE for mandatory courses)

GET    /subjects/{id}/see     Retrieve stored SEE record
```

### Marks Summary (main output endpoint)
```
GET    /semesters/{id}/marks-summary
Response: {
  semester_id, semester_number, academic_year,
  subjects: [{
    subject_id, subject_code, subject_name, subject_type,
    credits, is_mandatory,
    -- All CIE raw components:
    ia_test1_raw, ia_test2_raw, ia_scaled,
    cce_marks,
    lab_record_marks, lab_test1_raw, lab_test2_raw, lab_test_scaled,
    direct_cie_marks,
    -- Computed:
    final_cie,       -- /50 (or /100 for MC)
    is_detained,
    -- SEE:
    see_raw,         -- /100
    see_reduced,     -- /50
    is_absent,
    -- Overall:
    status           -- "Complete" | "CIE Only" | "Pending" | "Detained" | "Absent"
  }]
}
```

### Health
```
GET /health    → { "status": "ok", "version": "2.0.0" }
```

---

## 6. Frontend Architecture

Three files: `index.html`, `style.css`, `app.js`. No framework — pure vanilla JS.

### Wizard Steps (6 steps)
| Step | What happens |
|------|-------------|
| 1 | Student profile form → `POST /students/` |
| 2 | Semester details form → `POST /students/{id}/semesters/` |
| 3 | Add subjects: **Manual** (one-by-one form) OR **PDF upload** |
| 4 | Review subject types; user can correct auto-detected type via `PUT /subjects/{id}` |
| 5 | Click each subject → opens modal → enter marks → live CIE preview → save |
| 6 | Summary cards (all subjects, final CIE, SEE, total) + JSON export download |

### State Management (`state` object in `app.js`)
```js
state = {
  studentId: null,     // from step 1
  semesterId: null,    // from step 2
  subjects: [],        // [{id, subject_code, subject_name, subject_type, credits, ...}]
  marks: {},           // {subject_id: {cie_final, see_raw, see_reduced, status, ...}}
  mode: "manual",      // "manual" | "pdf"
  currentStep: 1,
}
```

### Modal Forms (in `buildMarksForm()`)
The modal dynamically renders different fields based on `subject_type`:
- **PCC/ESC/AEC/UHV/other:** IA Test 1, IA Test 2, CCE, SEE
- **IPCC:** IA Test 1, IA Test 2, CCE, Lab Record, Lab Test 1, Lab Test 2, SEE
- **PCCL:** Lab Record, Lab Test, SEE
- **MC:** Direct CIE marks (no SEE fields shown)

Live CIE preview (`livePreview()`) recalculates `final_cie` in the browser as the user types.

---

## 7. Key Files — Full Purpose

| File | Purpose |
|------|---------|
| `models.py` | ORM models: `Student`, `Semester`, `Subject`, `CIERecord`, `SEEMark`, `SubjectType` enum |
| `schemas.py` | Pydantic I/O: `SubjectCreate`, `CIERecordCreate`, `SEEMarkCreate`, `SubjectMarksSummary`, `SemesterMarksSummary` |
| `services/cie_calculator.py` | `compute_cie(subject_type, data_dict)` → returns all scaled fields. `is_detained(final_cie, is_mandatory)` |
| `services/subject_service.py` | `create_subject_from_row(row)` converts PDF row → subject dict. `upsert_subject(db, sem_id, data)` |
| `pdf_engine/structure_extractor.py` | `extract_subjects_from_pdf(bytes)` → `(list_of_subject_dicts, warnings)`. Contains `_infer_subject_type(code, name)` |
| `routers/marks.py` | `POST /subjects/{id}/cie` calls `compute_cie` + `is_detained` then upserts `CIERecord`. `POST /subjects/{id}/see` halves raw score. |
| `routers/results.py` | `GET /semesters/{id}/marks-summary` calls `_build_subject_summary()` for each subject → returns `SemesterMarksSummary` |
| `routers/syllabus.py` | Handles PDF multipart upload, calls `extract_subjects_from_pdf`, then `upsert_subject` for each row |
| `seed_db.py` | Standalone script to populate DB with 5 CSE students, III semester 2024-25, all subject types |

---

## 8. Setup Instructions

### Prerequisites
- Python 3.10+
- pip

### Install
```bash
cd "c:\SIC Hacakthon\academic_data_engine"
pip install -r requirements.txt
```

### First-time Run (with sample data)
```bash
# Start server (creates fresh academic.db automatically)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Open a second terminal and run the seeder once:
python seed_db.py
```

### Run (existing data)
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Open App
- **UI Wizard:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health

---

## 9. Pre-Seeded Database Contents

After running `seed_db.py`, the database contains:

**III Semester CSE — 2024-25 — 9 subjects per student:**

| Subject Code | Subject Name | Type | Credits |
|-------------|-------------|------|---------|
| BCS301 | Discrete Mathematical Structures | PCC | 3 |
| BCS302 | Analog and Digital Electronics | PCC | 3 |
| BCS303 | Data Structures | PCC | 3 |
| BCS304 | Computer Organization and Architecture | IPCC | 4 |
| BCSL305 | Data Structures Laboratory | PCCL | 1 |
| BCS356A | Biology for Engineers | ESC | 3 |
| BCS357B | Indian Constitution | AEC | 2 |
| BRMCK358 | Management and Entrepreneurship | MC | 0 |
| BUHK359 | Universal Human Values | UHV | 1 |

**Students:**

| USN | Name | Performance Note |
|-----|------|-----------------|
| 1RN22CS001 | Bhargav Reddy | Good — all complete |
| 1RN22CS002 | Priya Sharma | Excellent — near-max marks |
| 1RN22CS003 | Kiran Nair | Average |
| 1RN22CS004 | Ananya Bhat | BCS302 → **DETAINED** (CIE < 20) — tests the detention scenario |
| 1RN22CS005 | Rohit Verma | Above average |

---

## 10. Extension Ideas / Next Steps

Here's what could be built on top of this system:

| Feature | Where to add |
|---------|-------------|
| SGPA/CGPA calculation | New endpoint in `results.py` using grade table |
| Grade letters (S/A/B/C/D/F) | Add `compute_grade(total)` to `cie_calculator.py` |
| Export to Excel | New router using `openpyxl` |
| Multiple semesters CGPA | Aggregate across all semesters in student router |
| Student login / authentication | Add `FastAPI-Users` or JWT middleware |
| PostgreSQL instead of SQLite | Change `DATABASE_URL` in `database.py` |
| Deploy to cloud | Use `railway.app` or `render.com` (add `Procfile`) |
| Drag-and-drop PDF | Already supported in the upload zone |
| Bulk marks import from Excel | New router + `openpyxl` parser |

---

## 11. Dependencies (`requirements.txt`)

```
fastapi==0.109.2          # Web framework
uvicorn[standard]==0.27.1 # ASGI server
sqlalchemy==2.0.27        # ORM
pydantic==2.6.1           # Data validation
pdfplumber==0.10.3        # PDF table extraction (Strategy 1 & 2)
PyMuPDF==1.23.26          # PDF text extraction (Strategy 3 fallback)
python-multipart==0.0.9   # Multipart form handling (file upload)
Pillow==10.2.0            # Image processing (PDF)
aiofiles==23.2.1          # Async file handling
```

---

## 12. Known Limitations

1. **PDF extraction accuracy** depends on how the PDF is structured. Machine-readable PDFs with proper table borders work best. Scanned/image PDFs will not extract — manual entry fallback is always available.

2. **Subject type auto-detection** from PDF is heuristic (based on course code pattern). Users should review in Step 4 of the wizard.

3. **Single semester per student** — the UI wizard creates one semester at a time. Multiple semesters can be added via the API.

4. **No authentication** — anyone with network access to port 8000 can read/write all data. Fine for local/hackathon use.

5. **SQLite** is file-based. Not suitable for concurrent multi-user production. Switch to PostgreSQL for team use beyond localhost.

---

*Built for RNSIT 2024 Autonomous Scheme — February 2026*
