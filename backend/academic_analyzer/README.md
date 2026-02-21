# 🎓 Academic Performance Analysis Dashboard

A smart academic analysis system built for hackathons to help students understand performance, identify weaknesses, and plan improvements to achieve their target GPA.

---

## 🚀 What This Project Does

This dashboard goes beyond marks display.

It helps students:

✔ analyze academic performance  
✔ identify weak areas (exam vs internal performance)  
✔ prioritize subjects based on credit impact  
✔ simulate GPA improvement strategies  
✔ visualize study progress and trends  

---

## 📁 Project Structure

| File | Purpose |
|------|--------|
| `main_dashboard.py` | Streamlit app (UI, KPI cards, tabs, charts) |
| `performance_logic.py` | Weak subject detection, gap, priority, risk |
| `gpa_calculator.py` | Grade point scale & weighted GPA calculations |
| `analytics_charts.py` | Plotly visual analytics |
| `marks_calc.py` | SGPA calculation & subject grade points |
| `improve.py` | Performance diagnostics & improvement advice |
| `impact.py` | GPA improvement & CGPA impact simulation |

---

## ⚙️ Setup Instructions

### 1️⃣ Install Python
Recommended: **Python 3.10 – 3.12**

### 2️⃣ Install dependencies

```bash
pip install streamlit pandas numpy plotly