from fastapi import APIRouter, HTTPException
from models import StudentCreate, StudentUpdate
from database import get_db
from bson import ObjectId

router = APIRouter()


def _serialize(doc):
    if doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


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
