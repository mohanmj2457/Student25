"""
analytics_charts.py
All Plotly chart generators for the Academic Performance Analysis Dashboard.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


# ─────────────────────────────────────────────
# COLOUR PALETTE
# ─────────────────────────────────────────────
PRIMARY   = "#6C63FF"
SECONDARY = "#FF6584"
SUCCESS   = "#43E97B"
WARNING   = "#FA8231"
DANGER    = "#FF4757"
BG_DARK   = "#0F172A"
BG_CARD   = "#1E293B"
TEXT      = "#E2E8F0"
GRID      = "#334155"

PLOTLY_THEME = {
    "paper_bgcolor": BG_CARD,
    "plot_bgcolor":  BG_CARD,
    "font":          dict(color=TEXT, family="Inter, sans-serif"),
}


# ─────────────────────────────────────────────
# 1. BAR CHART – Daily Study Hours
# ─────────────────────────────────────────────

def bar_study_hours(df: pd.DataFrame) -> go.Figure:
    low_threshold = 2.0  # hours considered low
    colors = [
        DANGER if h < low_threshold else PRIMARY
        for h in df["Daily_Study_Hours"]
    ]
    fig = go.Figure(
        go.Bar(
            x=df["Subject"],
            y=df["Daily_Study_Hours"],
            marker_color=colors,
            text=df["Daily_Study_Hours"].apply(lambda h: f"{h}h"),
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Study Hours: %{y}h<extra></extra>",
        )
    )
    fig.add_hline(
        y=low_threshold,
        line_dash="dash",
        line_color=WARNING,
        annotation_text="Low-effort threshold (2h)",
        annotation_position="top right",
        annotation_font_color=WARNING,
    )
    fig.update_layout(
        **PLOTLY_THEME,
        title=dict(text="📘 Daily Study Hours per Subject", font=dict(size=16, color=TEXT)),
        xaxis=dict(title="Subject", gridcolor=GRID, tickfont=dict(size=11)),
        yaxis=dict(title="Hours / Day", gridcolor=GRID),
        margin=dict(t=60, b=40, l=40, r=20),
        showlegend=False,
    )
    return fig


# ─────────────────────────────────────────────
# 2. PIE CHART – Subject Credit Distribution
# ─────────────────────────────────────────────

def pie_credit_distribution(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        go.Pie(
            labels=df["Subject"],
            values=df["Credits"],
            hole=0,
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>Credits: %{value}<br>Weight: %{percent}<extra></extra>",
            marker=dict(
                colors=px.colors.qualitative.Vivid,
                line=dict(color=BG_DARK, width=2),
            ),
        )
    )
    fig.update_layout(
        **PLOTLY_THEME,
        title=dict(text="🎓 Subject Credit Distribution", font=dict(size=16, color=TEXT)),
        margin=dict(t=60, b=20, l=20, r=20),
        legend=dict(font=dict(color=TEXT)),
    )
    return fig


# ─────────────────────────────────────────────
# 3. DOUGHNUT CHART – Task Completion
# ─────────────────────────────────────────────

def doughnut_task_completion(df: pd.DataFrame) -> go.Figure:
    counts = df["Task_Status"].value_counts()
    labels = counts.index.tolist()
    values = counts.values.tolist()
    colors = [SUCCESS if l == "Completed" else SECONDARY for l in labels]

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.60,
            textinfo="label+value",
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>",
            marker=dict(colors=colors, line=dict(color=BG_DARK, width=3)),
        )
    )
    pct = round(counts.get("Completed", 0) / counts.sum() * 100, 1)
    fig.add_annotation(
        text=f"<b>{pct}%</b><br>Done",
        x=0.5, y=0.5,
        font=dict(size=20, color=TEXT),
        showarrow=False,
    )
    fig.update_layout(
        **PLOTLY_THEME,
        title=dict(text="✅ Task Completion Status", font=dict(size=16, color=TEXT)),
        margin=dict(t=60, b=20, l=20, r=20),
        legend=dict(font=dict(color=TEXT)),
    )
    return fig


# ─────────────────────────────────────────────
# 4. RADAR CHART – Performance Comparison
# ─────────────────────────────────────────────

def radar_performance(df: pd.DataFrame) -> go.Figure:
    subjects = df["Subject"].tolist()
    categories = subjects + [subjects[0]]  # close the polygon

    current = df["Current_Marks"].tolist() + [df["Current_Marks"].iloc[0]]
    target  = df["Target_Marks"].tolist()  + [df["Target_Marks"].iloc[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=target,
        theta=categories,
        fill="toself",
        name="Target Marks",
        line_color=SUCCESS,
        fillcolor=f"rgba(67,233,123,0.15)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=current,
        theta=categories,
        fill="toself",
        name="Current Marks",
        line_color=PRIMARY,
        fillcolor=f"rgba(108,99,255,0.25)",
    ))
    fig.update_layout(
        **PLOTLY_THEME,
        title=dict(text="📡 Performance Radar: Current vs Target", font=dict(size=16, color=TEXT)),
        polar=dict(
            bgcolor=BG_CARD,
            radialaxis=dict(visible=True, range=[0, 100], gridcolor=GRID, color=TEXT),
            angularaxis=dict(gridcolor=GRID, color=TEXT),
        ),
        legend=dict(font=dict(color=TEXT)),
        margin=dict(t=80, b=30, l=30, r=30),
    )
    return fig


# ─────────────────────────────────────────────
# 5. STACKED BAR – Current vs Target Marks
# ─────────────────────────────────────────────

def bar_marks_comparison(df: pd.DataFrame) -> go.Figure:
    """Grouped bar showing current vs target; weak subjects highlighted."""
    bar_colors_current = [
        DANGER if w else PRIMARY for w in df["Is_Weak"]
    ]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Current Marks",
        x=df["Subject"],
        y=df["Current_Marks"],
        marker_color=bar_colors_current,
        hovertemplate="<b>%{x}</b><br>Current: %{y}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Target Marks",
        x=df["Subject"],
        y=df["Target_Marks"],
        marker_color=SUCCESS,
        opacity=0.6,
        hovertemplate="<b>%{x}</b><br>Target: %{y}<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_THEME,
        barmode="group",
        title=dict(text="📊 Current vs Target Marks (🔴 = Weak Subject)", font=dict(size=16, color=TEXT)),
        xaxis=dict(title="Subject", gridcolor=GRID),
        yaxis=dict(title="Marks", gridcolor=GRID, range=[0, 110]),
        legend=dict(font=dict(color=TEXT)),
        margin=dict(t=60, b=40, l=40, r=20),
    )
    return fig


# ─────────────────────────────────────────────
# 6. CALENDAR HEATMAP – Study Consistency
# ─────────────────────────────────────────────

def calendar_heatmap_study(df: pd.DataFrame) -> go.Figure:
    """
    Simulates 28 days of study-hour data.
    GitHub-style green colorscale: dark = 0h, bright green = high hours.
    """
    np.random.seed(42)
    n_days = 28
    today = pd.Timestamp("2026-02-21")
    dates = [today - pd.Timedelta(days=i) for i in range(n_days - 1, -1, -1)]

    avg_hours = df["Daily_Study_Hours"].mean()
    daily_hours = []
    for _ in dates:
        base = np.random.choice(
            [0, avg_hours * 0.5, avg_hours, avg_hours * 1.5],
            p=[0.12, 0.20, 0.50, 0.18]
        )
        noise = np.random.uniform(-0.3, 0.5)
        daily_hours.append(max(0, round(base + noise, 1)))

    weeks = 4
    days_week = 7
    z    = np.array(daily_hours).reshape(weeks, days_week)
    day_labels  = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    week_labels = []
    for w in range(weeks):
        start = dates[w * 7].strftime("%b %d")
        end   = dates[w * 7 + 6].strftime("%b %d")
        week_labels.append(f"{start} – {end}")

    # Build hover text: date + hours
    hover = []
    for w in range(weeks):
        row_hover = []
        for d in range(days_week):
            day_date = dates[w * 7 + d].strftime("%a, %b %d")
            hrs = z[w, d]
            emoji = "🔥" if hrs >= 3.5 else ("📚" if hrs >= 2 else ("💤" if hrs == 0 else "✏️"))
            row_hover.append(f"<b>{day_date}</b><br>{emoji} {hrs}h studied")
        hover.append(row_hover)

    # GitHub-style green: no study = dark slate, max = vivid green
    github_green = [
        [0.00, "#161B22"],   # 0h — near black
        [0.15, "#0E4429"],   # very light activity
        [0.35, "#006D32"],   # low study
        [0.60, "#26A641"],   # moderate study
        [0.80, "#39D353"],   # good study
        [1.00, "#7EE787"],   # intense study
    ]

    fig = go.Figure(go.Heatmap(
        z=z,
        x=day_labels,
        y=week_labels,
        colorscale=github_green,
        text=hover,
        hovertemplate="%{text}<extra></extra>",
        showscale=True,
        colorbar=dict(
            title=dict(text="Study Hours", font=dict(color=TEXT, size=12)),
            tickfont=dict(color=TEXT),
            tickvals=[0, 1, 2, 3, 4],
            ticktext=["0h", "1h", "2h", "3h", "4h+"],
            bgcolor=BG_CARD,
            bordercolor=GRID,
            borderwidth=1,
        ),
        xgap=4,   # gap between cells
        ygap=4,
    ))
    fig.update_layout(
        **PLOTLY_THEME,
        title=dict(
            text="📅 Study Consistency Heatmap · 🟩 Darker green = More hours studied",
            font=dict(size=15, color=TEXT)
        ),
        xaxis=dict(side="top", tickfont=dict(color=TEXT, size=12), gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(autorange="reversed", tickfont=dict(color=TEXT, size=11), gridcolor="rgba(0,0,0,0)"),
        margin=dict(t=80, b=20, l=120, r=80),
    )
    return fig



# ─────────────────────────────────────────────
# 7. GPA IMPACT BAR
# ─────────────────────────────────────────────

def bar_gpa_impact(df_impact: pd.DataFrame) -> go.Figure:
    sorted_df = df_impact.sort_values("GPA_Impact", ascending=False)
    colors = [SUCCESS if v > 0 else SECONDARY for v in sorted_df["GPA_Impact"]]

    fig = go.Figure(go.Bar(
        x=sorted_df["Subject"],
        y=sorted_df["GPA_Impact"],
        marker_color=colors,
        text=sorted_df["GPA_Impact"].apply(lambda v: f"+{v}" if v >= 0 else str(v)),
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>GPA Impact: %{y}<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_THEME,
        title=dict(text="📈 Per-Subject GPA Impact (if Target Achieved)", font=dict(size=16, color=TEXT)),
        xaxis=dict(title="Subject", gridcolor=GRID),
        yaxis=dict(title="GPA Δ", gridcolor=GRID),
        margin=dict(t=60, b=40, l=40, r=20),
        showlegend=False,
    )
    return fig
