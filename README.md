# 🎓 Student Planner Suite

Welcome to the unified Student Planner Suite! This application manages both academic data tracking and advanced GPA analytics through a single Next.js unified login dashboard.

## Services

1. **Frontend Launchpad (Next.js)**: Runs on `http://localhost:9002`
2. **Academic Data Engine (FastAPI)**: Runs on `http://localhost:8000`
3. **Performance Analyzer (Streamlit)**: Runs on `http://localhost:8501`

## How to Start Everything

You no longer need to start 3 separate terminals. Simply run the unified launcher script:

### On Windows (PowerShell)
```powershell
.\start_planner.ps1
```

Once started, open `http://localhost:9002` in your browser to log in and select the tool you wish to use.

## Technical Details
This repository contains a Next.js `frontend` app and a 2-part Python `backend` (`academic_data_engine` for core storage/marks calculation, and `academic_analyzer` for simulation/priority reporting). 
