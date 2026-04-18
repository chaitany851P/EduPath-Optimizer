from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import os
from routers import students, teachers, admin, attendance, optimization, phase_2_3, auth
from database import connect_db, disconnect_db

# Absolute Path Resolution
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"

app = FastAPI(
    title="EduPath Optimizer API",
    description="Strategic AI Attendance Assistant for Professional Growth",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()

# API Routers
app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(teachers.router, prefix="/api/teachers", tags=["Teachers"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])
app.include_router(optimization.router, prefix="/api/optimize", tags=["Optimization"])
app.include_router(phase_2_3.router, prefix="/api/phase-2-3", tags=["Phase 2-3"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

# Static Files (CSS/JS)
app.mount("/static", StaticFiles(directory=TEMPLATES_DIR), name="static")

# Professional UI Routes
@app.get("/")
async def root():
    return FileResponse(TEMPLATES_DIR / "login.html")

@app.get("/login")
async def login_page():
    return FileResponse(TEMPLATES_DIR / "login.html")

@app.get("/student.html")
async def student_page():
    return FileResponse(TEMPLATES_DIR / "student.html")

@app.get("/teacher.html")
async def teacher_page():
    return FileResponse(TEMPLATES_DIR / "teacher.html")

@app.get("/admin.html")
async def admin_page():
    return FileResponse(TEMPLATES_DIR / "admin.html")

@app.get("/health")
async def health():
    return {"status": "healthy"}
