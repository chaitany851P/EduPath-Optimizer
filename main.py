from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import date, timedelta, datetime
import holidays
import math

# Initialize FastAPI App
app = FastAPI(
    title="EduPath Optimizer - Strategic Version",
    description="An AI-driven strategic attendance suggestion system for university students.",
    version="1.1.0"
)

# --- 1. CONFIGURATION: CAREER TRACKS & TIMETABLE ---
CAREER_TRACKS = {
    "Data Science": ["Python", "Statistics", "Machine Learning", "Data Mining"],
    "Cyber Security": ["Networking", "Cryptography", "Ethical Hacking", "Linux"],
    "IOT": ["Embedded Systems", "Sensors", "Microcontrollers", "C Programming"],
    "Computer Graphics": ["UI/UX", "Animation", "Rendering", "Game Dev"]
}

# Mock Timetable: 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri
WEEKLY_TIMETABLE = {
    0: ["Maths", "Python", "C Programming"],          # Monday
    1: ["Statistics", "Embedded Systems"],            # Tuesday
    2: ["Machine Learning", "Linux", "Animation"],    # Wednesday
    3: ["Data Mining", "Networking", "Sensors"],      # Thursday
    4: ["Cryptography", "UI/UX", "Ethics"]            # Friday
}

# --- 2. MODELS: INPUT DATA VALIDATION ---
class AttendanceInput(BaseModel):
    start_date: date = Field(..., description="Format: YYYY-MM-DD")
    end_date: date = Field(..., description="Format: YYYY-MM-DD")
    current_attended: int = Field(..., ge=0, description="Number of classes already attended")
    target_percentage: float = Field(default=75.0, ge=0, le=100, description="Minimum percentage required (0-100)")
    career_track: str = Field(default="Data Science", description="Chosen career path for prioritization")
    country_code: str = Field(default="IN", description="ISO Country Code for public holidays")

# --- 3. HELPER LOGIC: DATE CALCULATIONS & HOLIDAYS ---
def get_strategic_dates(start: date, end: date, country_code: str, track: str):
    if end < start:
        raise HTTPException(status_code=400, detail="End date cannot be before start date.")

    # Load public holidays for the specific years in range
    years = list(set([start.year, end.year]))
    all_holidays = holidays.CountryHoliday(country_code, years=years)
    
    target_subjects = CAREER_TRACKS.get(track, [])
    
    priority_days = []
    general_days = []
    
    current = start
    while current <= end:
        # Check if it's a weekday (0-4) and NOT a public holiday
        if current.weekday() < 5 and current not in all_holidays:
            day_subjects = WEEKLY_TIMETABLE.get(current.weekday(), [])
            # Check if any subject on this day matches the Career Track
            is_priority = any(sub in target_subjects for sub in day_subjects)
            
            if is_priority:
                priority_days.append(current)
            else:
                general_days.append(current)
        current += timedelta(days=1)
        
    return priority_days, general_days, all_holidays

# --- 4. MAIN ENDPOINT: STRATEGY CALCULATION ---
@app.get("/")
def health_check():
    return {"status": "online", "project": "EduPath Optimizer", "day": 4}

@app.post("/calculate-strategy")
def calculate_strategy(data: AttendanceInput):
    # Fetch categorized working days
    p_days, g_days, h_list = get_strategic_dates(
        data.start_date, data.end_date, data.country_code, data.career_track
    )
    
    total_working = p_days + g_days
    total_count = len(total_working)
    
    # Calculate target math
    # math.ceil ensures we always round up to the nearest whole class
    required_total = math.ceil((data.target_percentage / 100) * total_count)
    gap = max(0, required_total - data.current_attended)
    
    # Identify FUTURE dates (Today onwards)
    today = date.today()
    future_p = [d for d in p_days if d >= today]
    future_g = [d for d in g_days if d >= today]
    
    # Combine lists: Priority days first, then fill remaining gap with General days
    suggested_dates = (future_p + future_g)[:gap]

    # --- SMART AI REASONING LOGIC ---
    future_p_count = len(future_p)
    
    if gap == 0:
        logic_explanation = (
            f"You have already met your {data.target_percentage}% target. "
            f"No mandatory attendance needed, but there are {future_p_count} "
            f"career-critical classes remaining for your professional growth."
        )
    elif gap <= future_p_count:
        logic_explanation = (
            f"To hit your goal, you need {gap} more days. "
            f"We have suggested {gap} dates that are 100% aligned with your "
            f"{data.career_track} career track."
        )
    else:
        extra_days = gap - future_p_count
        logic_explanation = (
            f"To hit your goal, you need {gap} more days. We prioritized all "
            f"{future_p_count} career-critical classes, plus {extra_days} general "
            "classes to ensure you meet the university criteria."
        )

    return {
        "meta_data": {
            "career_track_selected": data.career_track,
            "total_semester_working_days": total_count,
            "today": str(today)
        },
        "attendance_math": {
            "current_attended": data.current_attended,
            "target_percentage": f"{data.target_percentage}%",
            "classes_required_total": required_total,
            "gap_to_fill": gap
        },
        "strategic_plan": {
            "count_of_dates_suggested": len(suggested_dates),
            "dates_to_attend": suggested_dates,
            "logic_explanation": logic_explanation
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)