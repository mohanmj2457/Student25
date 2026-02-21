# improve.py

"""
This module identifies performance weaknesses
and suggests improvement strategies.
"""

from marks_calc import calculate_total, grade_point


# ---------- Analyze weak component ----------
def component_analysis(sub):
    """
    Identify which component needs improvement.
    Returns (weak_area, advice)
    """

    # THEORY SUBJECT
    if sub["type"] == "theory":
        if sub["see"] < sub["ia"]:
            return "SEE", "Focus on exam preparation & problem solving"
        else:
            return "CIE", "Improve internal assessments & consistency"

    # THEORY + LAB COMPONENT
    elif sub["type"] == "integrated_lab":
        if sub["practical"] < 5:
            return "Practical", "Practice lab execution & viva"
        elif sub["see"] < sub["ia"]:
            return "SEE", "Strengthen theory understanding"
        else:
            return "CIE", "Improve lab records & participation"

    # LAB ONLY SUBJECT
    elif sub["type"] == "lab_only":
        if sub["practical"] < 10:
            return "Practical", "Practice lab experiments"
        else:
            return "Lab Work", "Improve lab performance"


# ---------- Generate advice for all subjects ----------
def generate_advice(subjects):
    """
    Returns a list of advice for each subject.
    """
    advice_list = []

    for sub in subjects:
        sub["total"] = calculate_total(sub)
        sub["gp"] = grade_point(sub["total"])

        weak_area, advice = component_analysis(sub)

        advice_list.append({
            "Subject": sub["name"],
            "Weak Area": weak_area,
            "Advice": advice
        })

    return advice_list