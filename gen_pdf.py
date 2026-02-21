"""
gen_pdf.py - Generate a valid sample syllabus PDF that the RNSIT Data Engine can parse.
Uses fpdf2 to create a real bordered table with proper headers that pdfplumber will detect.
"""
from fpdf import FPDF
import os

class SyllabusPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "RNSIT 2024 Autonomous Scheme", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 11)
        self.cell(0, 8, "Semester 3 - Course Structure", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

def create_sample_syllabus(filename):
    pdf = SyllabusPDF()
    pdf.add_page()

    # ── Table header ──────────────────────────────────────────────
    col_widths = [30, 90, 20, 30]
    headers = ["Course Code", "Course Title", "Credits", "L-T-P"]

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(200, 220, 255)
    for w, h in zip(col_widths, headers):
        pdf.cell(w, 8, h, border=1, fill=True)
    pdf.ln()

    # ── Subject rows ───────────────────────────────────────────────
    subjects = [
        ("BCS301",  "Discrete Mathematical Structures",  "3", "3-0-2"),
        ("BCS302",  "Analog and Digital Electronics",     "4", "3-0-2"),
        ("BCS303",  "Data Structures and Applications",   "3", "3-0-2"),
        ("BCS304",  "Computer Organization and Architecture", "3", "3-0-0"),
        ("BBEE305", "Biology for Engineers",              "3", "3-0-0"),
        ("BIC306",  "Indian Constitution",                "1", "1-0-0"),
        ("BCSL307", "Data Structures Laboratory",         "2", "0-0-2"),
        ("BME308",  "Management and Entrepreneurship",    "3", "3-0-0"),
        ("BUHV309", "Universal Human Values",             "1", "1-0-0"),
        ("BRMCK357","Mandatory Course - Environment",     "0", "0-0-0"),
    ]

    pdf.set_font("Helvetica", "", 9)
    pdf.set_fill_color(255, 255, 255)
    for row in subjects:
        for w, val in zip(col_widths, row):
            pdf.cell(w, 7, val, border=1)
        pdf.ln()

    pdf.output(filename)
    print(f"Successfully generated: {filename}")

if __name__ == "__main__":
    out_dir = r"c:\Users\SIC\Student planner\backend\academic_data_engine\frontend"
    create_sample_syllabus(os.path.join(out_dir, "sample_syllabus.pdf"))
    # Also write to the upload location
    create_sample_syllabus(r"c:\Users\SIC\Student planner\sample_syllabus_to_upload.pdf")
