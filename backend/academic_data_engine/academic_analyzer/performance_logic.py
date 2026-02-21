"""
performance_logic.py
Core performance analysis logic for Academic Performance Analysis Dashboard.
"""

import pandas as pd
import numpy as np


# ─────────────────────────────────────────────
# DUMMY DATASET
# ─────────────────────────────────────────────

def get_dummy_data() -> pd.DataFrame:
    """Return a demo dataset of student subject performance."""
    data = {
        "Subject": [
            "Mathematics",
            "Physics",
            "Chemistry",
            "Computer Science",
            "English",
            "Data Structures",
            "Statistics",
            "Electronics",
        ],
        "Current_Marks": [55, 72, 48, 85, 63, 40, 78, 67],
        "Target_Marks":  [80, 85, 70, 95, 75, 65, 88, 80],
        "Credits":       [4,  4,  3,  4,  2,  4,  3,  3],
        "Daily_Study_Hours": [2.0, 3.5, 1.5, 4.0, 2.5, 1.0, 3.0, 2.0],
        "Task_Status": [
            "Pending",
            "Completed",
            "Pending",
            "Completed",
            "Completed",
            "Pending",
            "Completed",
            "Pending",
        ],
    }
    return pd.DataFrame(data)


# ─────────────────────────────────────────────
# ANALYSIS LOGIC
# ─────────────────────────────────────────────

def calculate_improvement_gap(df: pd.DataFrame) -> pd.DataFrame:
    """Gap = Target - Current."""
    df = df.copy()
    df["Gap"] = df["Target_Marks"] - df["Current_Marks"]
    return df


def identify_weak_subjects(df: pd.DataFrame) -> pd.DataFrame:
    """
    A subject is weak if:
      - current_marks < 60, OR
      - gap > 10
    """
    df = df.copy()
    df["Is_Weak"] = (df["Current_Marks"] < 60) | (df["Gap"] > 10)
    return df


def classify_risk(gap: float) -> str:
    """Return risk level based on improvement gap."""
    if gap > 15:
        return "High Risk"
    elif 8 <= gap <= 15:
        return "Medium Risk"
    else:
        return "Low Risk"


def calculate_priority_score(df: pd.DataFrame) -> pd.DataFrame:
    """priority_score = gap × subject_credit; sort descending."""
    df = df.copy()
    df["Priority_Score"] = df["Gap"] * df["Credits"]
    df["Risk_Level"] = df["Gap"].apply(classify_risk)
    df = df.sort_values("Priority_Score", ascending=False).reset_index(drop=True)
    return df


def get_completion_percentage(df: pd.DataFrame) -> float:
    """Overall task completion %."""
    total = len(df)
    completed = (df["Task_Status"] == "Completed").sum()
    return round((completed / total) * 100, 1) if total > 0 else 0.0


def build_analysis_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run the full analysis pipeline:
    gap → weak subjects → priority → risk
    """
    df = calculate_improvement_gap(df)
    df = identify_weak_subjects(df)
    df = calculate_priority_score(df)
    return df


def get_highest_priority_subject(df: pd.DataFrame) -> str:
    """Return subject name with highest priority score."""
    analyzed = build_analysis_dataframe(df)
    return analyzed.iloc[0]["Subject"]


def get_weak_subject_count(df: pd.DataFrame) -> int:
    analyzed = build_analysis_dataframe(df)
    return int(analyzed["Is_Weak"].sum())
