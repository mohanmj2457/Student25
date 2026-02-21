# marks_calc.py

"""
This module handles:

1. Calculating total marks for different subject types
2. Converting marks into Grade Points (GP)
3. Calculating SGPA using credits
4. Generatng a subject-wise performance report
"""


# ---------- Convert marks to Grade Point ----------
def grade_point(marks):
    """Return grade point based on total marks."""
    if marks >= 90: return 10
    elif marks >= 80: return 9
    elif marks >= 70: return 8
    elif marks >= 60: return 7
    elif marks >= 50: return 6
    elif marks >= 40: return 5
    else: return 0


# ---------- Calculate total marks ----------
def calculate_total(sub):
    """
    Calculate total marks based on subject type.

    THEORY:
        IA(30) + CCE(20) + SEE(50)

    INTEGRATED LAB:
        IA + Lab Work + Practical + CCE + SEE

    LAB ONLY:
        Lab Work + Practical + SEE
    """

    if sub["type"] == "theory":
        return sub["ia"] + sub["cce"] + sub["see"]

    elif sub["type"] == "integrated_lab":
        return (
            sub["ia"]
            + sub["lab_work"]
            + sub["practical"]
            + sub["cce"]
            + sub["see"]
        )

    elif sub["type"] == "lab_only":
        return (
            sub["lab_work"]
            + sub["practical"]
            + sub["see"]
        )


# ---------- Calculate SGPA ----------
def calculate_sgpa(subjects):
    """
    SGPA = Σ(GP × credits) / total credits
    """
    total_points = 0
    total_credits = 0

    for sub in subjects:

        # Ignore non-credit subjects (like NSS)
        if sub["credits"] == 0:
            continue

        sub["total"] = calculate_total(sub)
        sub["gp"] = grade_point(sub["total"])

        total_points += sub["gp"] * sub["credits"]
        total_credits += sub["credits"]

    return round(total_points / total_credits, 2)


# ---------- Generate performance report ----------
def generate_report(subjects):
    """
    Returns:
    - subject-wise grade report
    - overall SGPA
    """
    report = []

    for sub in subjects:
        sub["total"] = calculate_total(sub)
        sub["gp"] = grade_point(sub["total"])

        report.append({
            "Subject": sub["name"],
            "Grade Point": sub["gp"],
            "Total Marks": sub["total"]
        })

    sgpa = calculate_sgpa(subjects)
    return report, sgpa