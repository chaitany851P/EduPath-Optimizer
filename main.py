from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from datetime import date, timedelta, datetime
import holidays
import math
from jose import JWTError, jwt
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# ─────────────────────────────────────────────
# 1. CONFIG & SECURITY
# ─────────────────────────────────────────────
SECRET_KEY = "SGP_PROJECT_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(title="EduPath Optimizer Pro")
templates = Jinja2Templates(directory="templates")

# ─────────────────────────────────────────────
# 2. MONGODB CONNECTION
# ─────────────────────────────────────────────
uri = "mongodb+srv://chaitany-thakar:85173221cP@cluster0.flpifkn.mongodb.net/?appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.edupath_db

career_collection    = db.get_collection("career_tracks")
timetable_collection = db.get_collection("timetables")
fest_collection      = db.get_collection("fests")
users_collection     = db.get_collection("users")

# ─────────────────────────────────────────────
# 3. PYDANTIC MODELS
# ─────────────────────────────────────────────
class FestInput(BaseModel):
    event_name: str
    event_date: date

class AttendanceUpdate(BaseModel):
    student_id: str
    attended_count: int = Field(..., ge=0)

class AttendanceInput(BaseModel):
    start_date: date
    end_date: date
    current_attended: int   = Field(..., ge=0)
    target_percentage: float = Field(default=75.0, ge=0, le=100)
    career_track: str       = Field(default="Data Science")
    country_code: str       = "IN"

# ─────────────────────────────────────────────
# 4. AUTH HELPERS
# ─────────────────────────────────────────────
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise exc
        user = users_collection.find_one({"username": username})
        if not user:
            raise exc
        return user
    except JWTError:
        raise exc

# ─────────────────────────────────────────────
# 5. CORE LOGIC
# ─────────────────────────────────────────────
def get_strategic_dates(start: date, end: date, country_code: str,
                        target_subjects: list, db_timetable: dict):
    years = list(set([start.year, end.year]))
    public_holidays = holidays.CountryHoliday(country_code, years=years)

    fest_cursor = fest_collection.find({})
    fest_dates = {
        datetime.strptime(f["date"], "%Y-%m-%d").date()
        for f in fest_cursor if "date" in f
    }

    priority_days, general_days = [], []
    current = start
    while current <= end:
        if (current.weekday() < 5
                and current not in public_holidays
                and current not in fest_dates):
            day_subjects = db_timetable.get(current.weekday(), [])
            if any(sub in target_subjects for sub in day_subjects):
                priority_days.append(current)
            else:
                general_days.append(current)
        current += timedelta(days=1)

    return priority_days, general_days, fest_dates

# ─────────────────────────────────────────────
# 6. PAGE ROUTES (serve HTML files)
# ─────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/admin.html", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/teacher.html", response_class=HTMLResponse)
async def teacher_page(request: Request):
    return templates.TemplateResponse("teacher.html", {"request": request})

@app.get("/student.html", response_class=HTMLResponse)
async def student_page(request: Request):
    return templates.TemplateResponse("student.html", {"request": request})

# ─────────────────────────────────────────────
# 7. API — Public
# ─────────────────────────────────────────────
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_collection.find_one({"username": form_data.username,
                                      "password": form_data.password})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid Credentials")
    token = create_access_token({"sub": user["username"], "role": user["role"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"],
        "name": user["name"]
    }

@app.post("/calculate-strategy")
def calculate_strategy(data: AttendanceInput):
    track_doc = career_collection.find_one({"name": data.career_track})
    if not track_doc:
        raise HTTPException(status_code=404, detail="Track not found")
    target_subjects = track_doc.get("subjects", [])

    timetable_cursor = timetable_collection.find({})
    db_timetable = {
        doc.get("day_index"): doc.get("subjects")
        for doc in timetable_cursor
        if doc.get("day_index") is not None
    }

    p_days, g_days, _ = get_strategic_dates(
        data.start_date, data.end_date,
        data.country_code, target_subjects, db_timetable
    )
    total_working_count = len(p_days) + len(g_days)

    required_total = math.ceil((data.target_percentage / 100) * total_working_count)
    gap = max(0, required_total - data.current_attended)

    today = date.today()
    future_p = [d for d in p_days if d >= today]
    future_g = [d for d in g_days if d >= today]
    total_future_available = len(future_p) + len(future_g)

    suggested_career_objs, suggested_buffer_objs = [], []
    if gap > 0:
        if gap <= len(future_p):
            suggested_career_objs = future_p[:gap]
        else:
            suggested_career_objs = future_p
            remaining_gap = gap - len(future_p)
            suggested_buffer_objs = future_g[:remaining_gap]

    formatted_career = [d.strftime("%d-%m-%Y") for d in suggested_career_objs]
    formatted_buffer  = [d.strftime("%d-%m-%Y") for d in suggested_buffer_objs]

    if gap == 0:
        explanation = (
            f"✅ Goal met! You are above {data.target_percentage}%. "
            f"No more mandatory classes needed."
        )
    elif gap > total_future_available:
        explanation = (
            f"⚠️ CRITICAL RISK: It is impossible to hit {data.target_percentage}%. "
            f"You need {gap} more classes, but only {total_future_available} days remain. "
            f"Attend all {total_future_available} days to get as close as possible. "
            f"Please meet your counselor immediately for further guidance."
        )
    else:
        explanation = (
            f"Strategic Plan: Attend {len(formatted_career)} career sessions "
            f"and {len(formatted_buffer)} buffer sessions to hit your target."
        )

    return {
        "meta_data": {
            "career_track": data.career_track,
            "total_working_days": total_working_count,
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

# ─────────────────────────────────────────────
# 8. API — Admin
# ─────────────────────────────────────────────
@app.post("/admin/add-fest")
async def admin_add_fest(fest: FestInput,
                         current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admins can add fests")
    fest_collection.insert_one({
        "name": fest.event_name,
        "date": str(fest.event_date)
    })
    return {"message": f"Fest '{fest.event_name}' added successfully."}

@app.get("/admin/fests")
async def list_fests(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    fests = [{"name": f["name"], "date": f["date"]}
             for f in fest_collection.find({}, {"_id": 0})]
    return {"fests": fests}


@app.get("/admin/students")
async def admin_list_students(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    students = [
        {
            "username": u["username"],
            "name": u["name"],
            "attended": u.get("attended", 0),
            "career_track": u.get("career_track", "N/A")
        }
        for u in users_collection.find({"role": "student"}, {"_id": 0, "password": 0})
    ]
    return {"students": students}

# ─────────────────────────────────────────────
# 9. API — Teacher
# ─────────────────────────────────────────────
@app.post("/teacher/update-attendance")
async def update_attendance(data: AttendanceUpdate,
                            current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only Teachers can update attendance")
    result = users_collection.update_one(
        {"username": data.student_id},
        {"$set": {"attended": data.attended_count}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": f"Attendance updated for {data.student_id}"}

@app.get("/teacher/students")
async def list_students(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Teachers only")
    students = [
        {
            "username": u["username"],
            "name": u["name"],
            "attended": u.get("attended", 0),
            "career_track": u.get("career_track", "N/A")
        }
        for u in users_collection.find({"role": "student"}, {"_id": 0, "password": 0})
    ]
    return {"students": students}

# ─────────────────────────────────────────────
# 10. API — Student
# ─────────────────────────────────────────────
@app.get("/student/strategy")
async def student_strategy(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Students only")

    start_d = date(2026, 1, 1)
    end_d   = date(2026, 5, 30)

    track_doc = career_collection.find_one({"name": current_user.get("career_track")})
    if not track_doc:
        raise HTTPException(status_code=404, detail="Career track not configured for this student")

    timetable_cursor = timetable_collection.find({})
    db_tt = {
        d.get("day_index"): d.get("subjects")
        for d in timetable_cursor
        if d.get("day_index") is not None
    }

    p_days, g_days, _ = get_strategic_dates(start_d, end_d, "IN",
                                             track_doc["subjects"], db_tt)
    total_working = len(p_days) + len(g_days)
    attended      = current_user.get("attended", 0)
    required      = math.ceil(0.75 * total_working)
    gap           = max(0, required - attended)

    today = date.today()
    f_p   = [d for d in p_days if d >= today]
    f_g   = [d for d in g_days if d >= today]

    suggested_p = [d.strftime("%d-%m-%Y") for d in f_p[:gap]]
    suggested_g = [d.strftime("%d-%m-%Y") for d in f_g[:max(0, gap - len(f_p))]]

    if gap == 0:
        explanation = "✅ Goal met! You are above 75%. Keep it up."
    elif gap > (len(f_p) + len(f_g)):
        explanation = "⚠️ CRITICAL: Target impossible. Please meet your counselor immediately."
    else:
        explanation = (
            f"Strategic Plan: Attend {len(suggested_p)} career "
            f"and {len(suggested_g)} buffer sessions."
        )

    return {
        "name":        current_user["name"],
        "track":       current_user.get("career_track"),
        "attended":    attended,
        "gap":         gap,
        "explanation": explanation,
        "p_dates":     suggested_p,
        "g_dates":     suggested_g
    }

# ─────────────────────────────────────────────
# 11. RUN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)