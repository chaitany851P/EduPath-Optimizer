from fastapi import APIRouter, HTTPException
from models import StudentCreate, StudentUpdate
from database import get_db
from bson import ObjectId
from datetime import date
import math

router = APIRouter()


def _serialize(doc):
    if doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


@router.get("/strategy/{username}")
async def get_student_strategy_legacy(username: str):
    """
    Get student strategy (Legacy logic)
    """
    db = get_db()
    user = await db.users.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Simplified logic similar to root main.py
    start_d = date(2026, 1, 1)
    end_d   = date(2026, 5, 30)
    
    # Mock some subjects and working days
    total_working = 100 
    attended      = user.get("attended", 0)
    required      = math.ceil(0.75 * total_working)
    gap           = max(0, required - attended)
    
    if gap == 0:
        explanation = "✅ Goal met! You are above 75%. Keep it up."
    else:
        explanation = f"Strategic Plan: Attend {gap} more sessions to hit your target."
        
    return {
        "name":        user.get("name"),
        "track":       user.get("career_track", "General"),
        "attended":    attended,
        "gap":         gap,
        "explanation": explanation,
        "p_dates":     [],
        "g_dates":     []
    }


@router.post("/", status_code=201)
async def create_student(student: StudentCreate):
    db = get_db()
    existing = await db.students.find_one({"student_id": student.student_id})
    if existing:
        raise HTTPException(status_code=400, detail="Student ID already exists")
    result = await db.students.insert_one(student.model_dump())
    return {"id": str(result.inserted_id), "message": "Student created successfully"}


@router.get("/")
async def list_students():
    db = get_db()
    students = []
    async for s in db.students.find():
        students.append(_serialize(s))
    return students


@router.get("/{student_id}")
async def get_student(student_id: str):
    db = get_db()
    student = await db.students.find_one({"student_id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return _serialize(student)


@router.put("/{student_id}")
async def update_student(student_id: str, update: StudentUpdate):
    db = get_db()
    data = {k: v for k, v in update.model_dump().items() if v is not None}
    result = await db.students.update_one({"student_id": student_id}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student updated successfully"}


@router.delete("/{student_id}")
async def delete_student(student_id: str):
    db = get_db()
    result = await db.students.delete_one({"student_id": student_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted successfully"}
