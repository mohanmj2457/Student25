"""
main_dashboard.py
Academic Performance Analysis Dashboard
Run with: streamlit run main_dashboard.py
"""

import streamlit as st
import pandas as pd

# ✅ our modules
from marks_calc import generate_report
from improve import generate_advice
from impact import simulate_improvement

# teammate modules (UNCHANGED)
from performance_logic import (
    get_dummy_data,
    build_analysis_dataframe,
    get_completion_percentage,
    get_highest_priority_subject,
    get_weak_subject_count,
)

from gpa_calculator import (
    calculate_current_gpa,
    calculate_target_gpa,
    calculate_gpa_impact,
)

from analytics_charts import (
    bar_study_hours,
    pie_credit_distribution,
    doughnut_task_completion,
    radar_performance,
    bar_marks_comparison,
    calendar_heatmap_study,
    bar_gpa_impact,
)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Academic Performance Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## 🎓 Academic Dashboard")

    target_gpa_goal = st.slider("Target GPA", 5.0, 10.0, 8.5, 0.1)

    st.markdown("### 📝 Edit Subject Data")
    base_df = get_dummy_data()
    edited_df = st.data_editor(base_df, use_container_width=True, hide_index=True)

# ---------------- DATA PIPELINE ----------------
analyzed_df = build_analysis_dataframe(edited_df)
impact_df   = calculate_gpa_impact(analyzed_df)

# Dashboard GPA calculations
current_gpa    = calculate_current_gpa(analyzed_df)
achievable_gpa = calculate_target_gpa(analyzed_df)
target_gpa     = target_gpa_goal
gpa_gap        = round(target_gpa - current_gpa, 2)

# ⚠️ Convert dashboard dataframe → compatible format for our modules
subjects = []
for _, row in analyzed_df.iterrows():
    subjects.append({
        "name": row["Subject"],
        "type": "theory",     # safe default
        "ia": 0,
        "cce": 0,
        "see": row["Current_Marks"],
        "lab_work": 0,
        "practical": 0,
        "credits": row["Credits"]
    })

# -------- our module outputs --------
report, sgpa = generate_report(subjects)
advice_df = pd.DataFrame(generate_advice(subjects))

current_sgpa_sim, impact_sim = simulate_improvement(
    subjects,
    current_cgpa=current_gpa,
    completed_credits=60
)
impact_sim_df = pd.DataFrame(impact_sim)

# -------- extra analytics --------
weak_count     = get_weak_subject_count(edited_df)
top_priority   = get_highest_priority_subject(edited_df)
completion_pct = get_completion_percentage(analyzed_df)

# ---------------- HEADER ----------------
st.title("🎓 Academic Performance Dashboard")

# ---------------- KPI CARDS ----------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("Current GPA", current_gpa)
c2.metric("Target GPA", target_gpa, delta=gpa_gap)
c3.metric("Weak Subjects", weak_count)
c4.metric("Task Completion", f"{completion_pct}%")

st.markdown("---")

# ---------------- TABS ----------------
tab_overview, tab_analytics, tab_priority = st.tabs(
    ["Overview", "Analytics", "Priority Analysis"]
)

# ---------- TAB 1 ----------
with tab_overview:
    col1, col2 = st.columns(2)
    col1.plotly_chart(bar_marks_comparison(analyzed_df), use_container_width=True)
    col2.plotly_chart(radar_performance(analyzed_df), use_container_width=True)

    col3, col4 = st.columns(2)
    col3.plotly_chart(bar_study_hours(analyzed_df), use_container_width=True)
    col4.plotly_chart(doughnut_task_completion(analyzed_df), use_container_width=True)

# ---------- TAB 2 ----------
with tab_analytics:
    col5, col6 = st.columns(2)
    col5.plotly_chart(pie_credit_distribution(analyzed_df), use_container_width=True)
    col6.plotly_chart(bar_gpa_impact(impact_df), use_container_width=True)

    st.plotly_chart(calendar_heatmap_study(analyzed_df), use_container_width=True)

# ---------- TAB 3 ----------
with tab_priority:

    st.subheader("Subject Priority Ranking")
    st.dataframe(analyzed_df, use_container_width=True)

    # ✅ OUR ADDITIONS (safe)
    st.subheader("Academic Diagnostics")
    st.dataframe(advice_df, use_container_width=True)

    st.subheader("GPA Improvement Simulation")
    st.dataframe(impact_sim_df, use_container_width=True)

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("Academic Performance Dashboard • Hackathon Demo")