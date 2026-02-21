"""
gpa_calculator.py
GPA calculation utilities for Academic Performance Analysis Dashboard.
"""

import pandas as pd


# ─────────────────────────────────────────────
# GRADE POINT CONVERSION
# ─────────────────────────────────────────────

def marks_to_grade_point(marks: float) -> float:
    """Convert marks to grade point on a 10-point scale."""
    if marks >= 90:
        return 10
    elif marks >= 80:
        return 9
    elif marks >= 70:
        return 8
    elif marks >= 60:
        return 7
    elif marks >= 50:
        return 6
    elif marks >= 40:
        return 5
    else:
        return 0


# ─────────────────────────────────────────────
# GPA CALCULATIONS
# ─────────────────────────────────────────────

def calculate_gpa(marks_series: pd.Series, credits_series: pd.Series) -> float:
    """
    Weighted GPA = Σ(grade_point × credit) / Σ(credits)
    """
    grade_points = marks_series.apply(marks_to_grade_point)
    total_weighted = (grade_points * credits_series).sum()
    total_credits = credits_series.sum()
    if total_credits == 0:
        return 0.0
    return round(total_weighted / total_credits, 2)


def calculate_current_gpa(df: pd.DataFrame) -> float:
    return calculate_gpa(df["Current_Marks"], df["Credits"])


def calculate_target_gpa(df: pd.DataFrame) -> float:
    return calculate_gpa(df["Target_Marks"], df["Credits"])


# ─────────────────────────────────────────────
# PER-SUBJECT GPA IMPACT
# ─────────────────────────────────────────────

def calculate_gpa_impact(df: pd.DataFrame) -> pd.DataFrame:
    """
    GPA impact = (target_grade_point - current_grade_point) × credit / Σ(credits)
    Shows how much each subject contributes to the overall GPA improvement.
    """
    df = df.copy()
    df["Current_Grade_Point"] = df["Current_Marks"].apply(marks_to_grade_point)
    df["Target_Grade_Point"]  = df["Target_Marks"].apply(marks_to_grade_point)
    total_credits = df["Credits"].sum()
    df["GPA_Impact"] = round(
        (df["Target_Grade_Point"] - df["Current_Grade_Point"]) * df["Credits"] / total_credits,
        3,
    )
    return df
