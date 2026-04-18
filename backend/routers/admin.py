from fastapi import APIRouter, HTTPException, Depends, Request
from models import UniversityEvent, Role
from database import get_db
from typing import List

router = APIRouter()


def _serialize(doc):
    if doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


def verify_admin(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = auth_header.split(" ")[1]
    try:
        from jose import jwt
        from config import settings
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: Admin access required")


@router.post("/events/", status_code=201)
async def create_event(event: UniversityEvent, _=Depends(verify_admin)):
    db = get_db()
    data = event.model_dump()
    data["event_date"] = data["event_date"].isoformat()
    result = await db.events.insert_one(data)
    return {"id": str(result.inserted_id), "message": "Event added successfully"}


@router.post("/add-fest", status_code=201)
async def add_fest_legacy(event: UniversityEvent, _=Depends(verify_admin)):
    """Legacy alias for adding events"""
    return await create_event(event)


@router.get("/events/")
async def list_events():
    db = get_db()
    events = []
    async for e in db.events.find():
        events.append(_serialize(e))
    return events


@router.get("/fests")
async def list_fests_legacy():
    """Legacy alias for listing events"""
    events = await list_events()
    return {"fests": [{"name": e.get("title"), "date": e.get("event_date")} for e in events]}


@router.get("/students")
async def admin_list_students(_=Depends(verify_admin)):
    """List all students for admin dashboard"""
    db = get_db()
    students = []
    async for u in db.users.find({"role": "student"}, {"_id": 0, "password_hash": 0}):
        students.append(u)
    return {"students": students}


@router.delete("/events/{event_id}")
async def delete_event(event_id: str):
    from bson import ObjectId
    db = get_db()
    try:
        result = await db.events.delete_one({"_id": ObjectId(event_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid event ID")
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted successfully"}


@router.post("/semester/")
async def set_semester(start_date: str, end_date: str, name: str = "Semester"):
    db = get_db()
    await db.config.update_one(
        {"key": "semester"},
        {"$set": {"key": "semester", "name": name, "start_date": start_date, "end_date": end_date}},
        upsert=True,
    )
    return {"message": "Semester window configured"}


@router.get("/semester/")
async def get_semester():
    db = get_db()
    config = await db.config.find_one({"key": "semester"})
    if not config:
        raise HTTPException(status_code=404, detail="Semester not configured")
    config.pop("_id", None)
    return config
