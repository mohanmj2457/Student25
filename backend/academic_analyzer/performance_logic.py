"""
performance_logic.py
Core performance analysis logic for Academic Performance Analysis Dashboard.
"""

import pandas as pd
import numpy as np
import sqlite3
import os


import sqlite3
import os

# ─────────────────────────────────────────────
# LIVE DATABASE INTEGRATION
# ─────────────────────────────────────────────

def get_db_path():
    """Returns the absolute path to the academic_data_engine SQLite database."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "academic_data_engine", "academic.db")

def get_all_students() -> list[dict]:
    """Fetch a list of all students (Name, USN) from the DB."""
    db_path = get_db_path()
    if not os.path.exists(db_path):
        return []
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, usn FROM students ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_db_data(student_usn: str) -> pd.DataFrame:
    """Fetch real performance data for a specific student from SQLite."""
    db_path = get_db_path()
    
    if not os.path.exists(db_path):
        # Fallback if DB doesn't exist
        print("Warning: Database not found. Returning empty DataFrame.")
        return pd.DataFrame()
        
    conn = sqlite3.connect(db_path)
    
    # Query that joins students -> semesters -> subjects -> marks 
    query = """
    SELECT 
        s.subject_name as Subject,
        s.credits as Credits,
        COALESCE(c.final_cie, 0) as CIE,
        COALESCE(sm.reduced_scored, 0) as SEE
    FROM students st
    JOIN semesters sem ON sem.student_id = st.id
    JOIN subjects s ON s.semester_id = sem.id
    LEFT JOIN cie_records c ON c.subject_id = s.id
    LEFT JOIN see_marks sm ON sm.subject_id = s.id
    WHERE st.usn = ?
    """
    
    df = pd.read_sql_query(query, conn, params=(student_usn,))
    conn.close()
    
    if df.empty:
        return pd.DataFrame()

    # Calculate current marks out of 100
    df["Current_Marks"] = df["CIE"] + df["SEE"]
    
    # Add dummy target data (since targets aren't stored in DB yet)
    df["Target_Marks"] = 85
    
    dummy_hours = [2.0, 3.5, 1.5, 4.0, 2.5, 1.0, 3.0, 2.0]
    if len(df) > len(dummy_hours):
        dummy_hours.extend([2.0] * (len(df) - len(dummy_hours)))
    df["Daily_Study_Hours"] = dummy_hours[:len(df)] if len(df) > 0 else []

    df["Task_Status"] = "Pending"
    
    return df



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
