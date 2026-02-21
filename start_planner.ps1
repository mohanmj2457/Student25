# start_planner.ps1
# Unified Launcher for the Student Planner Application Suite

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "   🎓 Starting Student Planner Suite 🎓   " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Define the paths
$FrontendPath = ".\frontend"
$EnginePath = ".\backend\academic_data_engine"
$AnalyzerPath = ".\backend\academic_analyzer"

# Stop any running processes on our ports (Optional but helpful for clean starts)
# Not strictly necessary for this run but good practice

Write-Host "`n[1/3] Starting Next.js Frontend (Port 9002)..." -ForegroundColor Yellow
Start-Process -FilePath "npm.cmd" -ArgumentList "run dev -- --turbopack -p 9002" -WorkingDirectory $FrontendPath

Write-Host "[2/3] Starting Academic Data Engine (Port 8000)..." -ForegroundColor Yellow
Start-Process -FilePath "python" -ArgumentList "-m uvicorn main:app --port 8000 --reload" -WorkingDirectory $EnginePath

Write-Host "[3/3] Starting Academic Performance Analyzer (Port 8501)..." -ForegroundColor Yellow
Start-Process -FilePath "python" -ArgumentList "-m streamlit run main_dashboard.py --server.headless true" -WorkingDirectory $AnalyzerPath

Write-Host "`n✅ All services started successfully!" -ForegroundColor Green
Write-Host "-----------------------------------------"
Write-Host "🌐 Login Dashboard: http://localhost:9002"
Write-Host "🌐 Data Engine UI:  http://localhost:8000"
Write-Host "🌐 Analyzer UI:     http://localhost:8501"
Write-Host "-----------------------------------------"
Write-Host "Press Ctrl+C to exit this script (note: background processes will keep running until manually killed or terminals closed)." -ForegroundColor Gray

# Automatically open the React frontend in the default browser
Write-Host "`nOpening Next.js Frontend in your browser..." -ForegroundColor Yellow
Start-Sleep -Seconds 3 # Give Next.js a moment to spin up
Start-Process "http://localhost:9002"
