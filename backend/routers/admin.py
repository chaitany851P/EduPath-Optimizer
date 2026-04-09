from fastapi import APIRouter, HTTPException
from models import UniversityEvent
from database import get_db

router = APIRouter()


def _serialize(doc):
    if doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


@router.post("/events/", status_code=201)
async def create_event(event: UniversityEvent):
    db = get_db()
    data = event.model_dump()
    data["event_date"] = data["event_date"].isoformat()
    result = await db.events.insert_one(data)
    return {"id": str(result.inserted_id), "message": "Event added successfully"}


@router.get("/events/")
async def list_events():
    db = get_db()
    events = []
    async for e in db.events.find():
        events.append(_serialize(e))
    return events


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
