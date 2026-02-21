"""
main.py – FastAPI entry point (RNSIT 2024 Scheme — Final Version)
"""
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import engine, Base
from routers import student, semester, subjects, syllabus, marks, results

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s – %(message)s",
)
logger = logging.getLogger(__name__)

# Create / migrate all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RNSIT Academic Data Engine",
    description="CIE + SEE marks engine for RNSIT 2024 Autonomous Scheme",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(student.router)
app.include_router(semester.router)
app.include_router(subjects.router)
app.include_router(syllabus.router)
app.include_router(marks.router)
app.include_router(results.router)

# Serve frontend
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/", include_in_schema=False)
    async def root():
        return FileResponse(
            os.path.join(FRONTEND_DIR, "index.html"),
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate, public, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0",
            }
        )

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "version": "2.0.0"}
