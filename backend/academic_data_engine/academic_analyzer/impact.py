# impact.py

"""
This module simulates improvement in grades
and shows how SGPA & CGPA will improve.
"""

from marks_calc import calculate_sgpa, calculate_total, grade_point


# ---------- Next grade boundary ----------
def next_grade_target(gp):
    """
    Returns the minimum marks needed to reach next GP.
    """
    targets = {5: 60, 6: 70, 7: 80, 8: 90, 9: 100}
    return targets.get(gp)


# ---------- Simulate improvement ----------
def simulate_improvement(subjects, current_cgpa, completed_credits):
    """
    Shows how improving subjects affects:
    - Subject GP
    - SGPA
    - CGPA
    """

    results = []
    current_sgpa = calculate_sgpa(subjects)

    for sub in subjects:

        sub["total"] = calculate_total(sub)
        old_gp = grade_point(sub["total"])

        # skip if already highest grade
        if old_gp == 10:
            continue

        target_marks = next_grade_target(old_gp)

        # simulate improvement
        sub["total"] = target_marks
        new_gp = grade_point(target_marks)

        new_sgpa = calculate_sgpa(subjects)

        # CGPA update formula
        new_cgpa = ((current_cgpa * completed_credits) +
                    (new_sgpa * 20)) / (completed_credits + 20)

        results.append({
            "Subject": sub["name"],
            "GP Change": f"{old_gp} → {new_gp}",
            "New SGPA": round(new_sgpa, 2),
            "New CGPA": round(new_cgpa, 2)
        })

    return current_sgpa, results