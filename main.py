from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import date, timedelta, datetime
import holidays
import math
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# --- 1. INITIALIZATION ---
app = FastAPI(
    title="EduPath Optimizer",
    description="Strategic Attendance System with MongoDB and Admin Fest Management",
    version="1.2.0"
)

# --- 2. MONGODB CONNECTION ---
# Using your provided URI
uri = "mongodb+srv://chaitany-thakar:85173221cP@cluster0.flpifkn.mongodb.net/?appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.edupath_db

# Collections
career_collection = db.get_collection("career_tracks")
timetable_collection = db.get_collection("timetables")
fest_collection = db.get_collection("fests")

# --- 3. MODELS (Pydantic) ---
class AttendanceInput(BaseModel):
    start_date: date
    end_date: date
    current_attended: int = Field(..., ge=0)
    target_percentage: float = Field(default=75.0, ge=0, le=100)
    career_track: str = Field(default="Data Science")
    country_code: str = "IN"

class FestInput(BaseModel):
    event_name: str
    event_date: date

# --- 4. HELPER LOGIC ---
def get_strategic_dates(start: date, end: date, country_code: str, target_subjects: list, db_timetable: dict):
    # Fetch public holidays for the range
    years = list(set([start.year, end.year]))
    public_holidays = holidays.CountryHoliday(country_code, years=years)
    
    # Fetch University Fests from MongoDB
    fest_cursor = fest_collection.find({})
    fest_dates = {datetime.strptime(f["date"], "%Y-%m-%d").date() for f in fest_cursor if "date" in f}
    
    priority_days = []
    general_days = []
    
    current = start
    while current <= end:
        # Working Day Check: Not Weekend + Not Holiday + Not Fest
        if current.weekday() < 5 and current not in public_holidays and current not in fest_dates:
            day_subjects = db_timetable.get(current.weekday(), [])
            is_priority = any(sub in target_subjects for sub in day_subjects)
            
            if is_priority:
                priority_days.append(current)
            else:
                general_days.append(current)
        current += timedelta(days=1)
        
    return priority_days, general_days, fest_dates

# --- 5. ADMIN ENDPOINTS ---
@app.post("/admin/add-fest", tags=["Admin"])
def add_fest(fest: FestInput):
    """Teachers use this to add University Events/Fests as holidays."""
    fest_data = {
        "name": fest.event_name,
        "date": str(fest.event_date)
    }
    fest_collection.insert_one(fest_data)
    return {"message": f"Event '{fest.event_name}' added successfully."}

# --- 6. STUDENT STRATEGY ENDPOINTS ---
@app.get("/", tags=["General"])
def health_check():
    return {"status": "EduPath Optimizer Online", "phase": 1}

@app.post("/calculate-strategy", tags=["Student"])
def calculate_strategy(data: AttendanceInput):
    # 1. Fetch Career Track Data from DB
    track_doc = career_collection.find_one({"name": data.career_track})
    if not track_doc:
        raise HTTPException(status_code=404, detail=f"Career track '{data.career_track}' not found.")
    target_subjects = track_doc.get("subjects", [])

    # 2. Fetch Timetable Data safely (Prevents KeyError)
    timetable_cursor = timetable_collection.find({})
    db_timetable = {}
    for doc in timetable_cursor:
        idx = doc.get("day_index")
        subs = doc.get("subjects")
        if idx is not None and subs is not None:
            db_timetable[idx] = subs

    if not db_timetable:
        raise HTTPException(status_code=500, detail="University timetable is empty in database.")

    # 3. Calculate working days and priority dates
    p_days, g_days, f_dates = get_strategic_dates(
        data.start_date, data.end_date, data.country_code, target_subjects, db_timetable
    )
    
    total_working_count = len(p_days) + len(g_days)
    
    # 4. Math Logic
    required_total = math.ceil((data.target_percentage / 100) * total_working_count)
    gap = max(0, required_total - data.current_attended)
    
    # 5. Strategic Categorization (Prioritize future career dates)
    today = date.today()
    future_p = [d for d in p_days if d >= today]
    future_g = [d for d in g_days if d >= today]
    
    suggested_career = []
    suggested_buffer = []

    if gap > 0:
        if gap <= len(future_p):
            suggested_career = future_p[:gap]
        else:
            suggested_career = future_p
            remaining_gap = gap - len(future_p)
            suggested_buffer = future_g[:remaining_gap]

    # 6. Smart Reasoning Message
    total_suggested = len(suggested_career) + len(suggested_buffer)

    if gap == 0:
        explanation = f"Goal met! You are above {data.target_percentage}%. No mandatory classes needed."
    elif total_suggested < gap:
        # IMPOSSIBLE CASE
        explanation = (
            f"⚠️ ATTENDANCE RISK: It is mathematically impossible to hit {data.target_percentage}%. "
            f"Even if you attend all {total_suggested} remaining days, you will still be "
            f"{gap - total_suggested} classes short. Contact your Counsellor."
        )
    else:
        explanation = f"Plan: Attend {len(suggested_career)} career sessions and {len(suggested_buffer)} general sessions."

    return {
        "meta_data": {
            "career_track": data.career_track,
            "total_working_days": total_working_count,
            "fests_found_in_range": len([f for f in f_dates if data.start_date <= f <= data.end_date])
        },
        "attendance_math": {
            "current_attended": data.current_attended,
            "target_required": required_total,
            "gap_to_fill": gap
        },
        "strategic_plan": {
            "logic_explanation": explanation,
            "career_priority_dates": suggested_career,
            "buffer_attendance_dates": suggested_buffer
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)