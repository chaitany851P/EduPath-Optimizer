from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routers import students, teachers, admin, attendance, optimization, phase_2_3
from database import connect_db, disconnect_db

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

app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(teachers.router, prefix="/api/teachers", tags=["Teachers"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])
app.include_router(optimization.router, prefix="/api/optimize", tags=["Optimization"])
app.include_router(phase_2_3.router, prefix="/api/phase-2-3", tags=["Phase 2-3: Exam Strategy & Academic Bridge"])

@app.get("/")
async def root():
    return {"message": "EduPath Optimizer API is running (Phase 1-3)", "version": "2.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
