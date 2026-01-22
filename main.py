from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from datetime import date, timedelta, datetime
import holidays
import math
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# --- 1. INITIALIZATION ---
app = FastAPI(title="EduPath Optimizer")

# Setup Templates folder for Frontend
templates = Jinja2Templates(directory="templates")

# --- 2. MONGODB CONNECTION ---
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

# --- 5. FRONTEND ROUTE ---
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serves the Dashboard UI"""
    return templates.TemplateResponse("index.html", {"request": request})

# --- 6. ADMIN ENDPOINTS ---
@app.post("/admin/add-fest")
def add_fest(fest: FestInput):
    """Teachers use this to add University Events/Fests"""
    fest_data = {
        "name": fest.event_name,
        "date": str(fest.event_date)
    }
    fest_collection.insert_one(fest_data)
    return {"message": f"Event '{fest.event_name}' added successfully."}

# --- 7. STUDENT STRATEGY ENDPOINT ---
@app.post("/calculate-strategy")
def calculate_strategy(data: AttendanceInput):
    # 1. Database Fetching
    track_doc = career_collection.find_one({"name": data.career_track})
    if not track_doc:
        raise HTTPException(status_code=404, detail="Track not found")
    target_subjects = track_doc.get("subjects", [])

    timetable_cursor = timetable_collection.find({})
    db_timetable = {doc.get("day_index"): doc.get("subjects") for doc in timetable_cursor if doc.get("day_index") is not None}

    # 2. Get ALL working days for the Full Semester
    p_days, g_days, f_dates = get_strategic_dates(
        data.start_date, data.end_date, data.country_code, target_subjects, db_timetable
    )
    total_working_count = len(p_days) + len(g_days)

    # 3. Attendance Math
    required_total = math.ceil((data.target_percentage / 100) * total_working_count)
    gap = max(0, required_total - data.current_attended)

    # 4. Filter for FUTURE dates only
    today = date.today()
    future_p = [d for d in p_days if d >= today]
    future_g = [d for d in g_days if d >= today]
    total_future_available = len(future_p) + len(future_g)

    # 5. Build the Plan & Format Dates to DD-MM-YYYY
    suggested_career_objs = []
    suggested_buffer_objs = []

    if gap > 0:
        if gap <= len(future_p):
            suggested_career_objs = future_p[:gap]
        else:
            suggested_career_objs = future_p
            remaining_gap = gap - len(future_p)
            suggested_buffer_objs = future_g[:remaining_gap]

    # Convert date objects to DD-MM-YYYY strings
    formatted_career = [d.strftime("%d-%m-%Y") for d in suggested_career_objs]
    formatted_buffer = [d.strftime("%d-%m-%Y") for d in suggested_buffer_objs]

    # 6. Smart Reasoning + Counselor Warning
    if gap == 0:
        explanation = f"Goal met! You are above {data.target_percentage}%. No more mandatory classes needed."
    elif gap > total_future_available:
        # THE IMPOSSIBLE CASE + COUNSELOR WARNING
        explanation = (
            f"⚠️ CRITICAL RISK: It is impossible to hit {data.target_percentage}%. "
            f"You need {gap} more classes, but only {total_future_available} days remain. "
            f"Attend all {total_future_available} days to get as close as possible. "
            f"Please meet your counselor immediately for further guidance."
        )
    else:
        explanation = f"Strategic Plan: Attend {len(formatted_career)} career sessions and {len(formatted_buffer)} buffer sessions to hit your target."

    return {
        "meta_data": {
            "career_track": data.career_track,
            "total_working_days": total_working_count, # Matching frontend key
            "days_remaining": total_future_available
        },
        "attendance_math": {
            "current_attended": data.current_attended,
            "gap_to_fill": gap
        },
        "strategic_plan": {
            "logic_explanation": explanation,
            "career_priority_dates": formatted_career,
            "buffer_attendance_dates": formatted_buffer
        }
    }
# --- 8. RUN APP ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)