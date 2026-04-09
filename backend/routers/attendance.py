from fastapi import APIRouter, HTTPException
from models import AttendanceRecord
from database import get_db

router = APIRouter()


def _serialize(doc):
    if doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


@router.post("/", status_code=201)
async def record_attendance(record: AttendanceRecord):
    db = get_db()
    data = record.model_dump()
    data["date"] = data["date"].isoformat()
    # Upsert: one record per student/subject/date
    await db.attendance.update_one(
        {
            "student_id": data["student_id"],
            "subject_code": data["subject_code"],
            "date": data["date"],
        },
        {"$set": data},
        upsert=True,
    )
    return {"message": "Attendance recorded"}


@router.get("/{student_id}")
async def get_student_attendance(student_id: str):
    db = get_db()
    records = []
    async for r in db.attendance.find({"student_id": student_id}):
        records.append(_serialize(r))
    return records


@router.get("/{student_id}/{subject_code}/summary")
async def get_subject_summary(student_id: str, subject_code: str):
    db = get_db()
    total = await db.attendance.count_documents(
        {"student_id": student_id, "subject_code": subject_code}
    )
    present = await db.attendance.count_documents(
        {"student_id": student_id, "subject_code": subject_code, "status": "present"}
    )
    percentage = round((present / total * 100), 2) if total > 0 else 0
    return {
        "student_id": student_id,
        "subject_code": subject_code,
        "total_classes": total,
        "classes_attended": present,
        "attendance_percentage": percentage,
        "is_safe": percentage >= 75,
    }
