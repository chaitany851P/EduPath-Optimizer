from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from models import OptimizationRequest, OptimizationResponse, DateClassification, CareerTrack
from database import get_db
from datetime import date, datetime, timedelta
import math
import holidays

router = APIRouter()

# Career track → high-priority subject keywords
CAREER_SUBJECT_MAP = {
    "AI & ML": ["python", "ml", "machine learning", "neural", "data science"],
    "Cyber Security": ["security", "network", "cryptography", "ethical", "cyber"],
    "Web Dev": ["web", "html", "css", "javascript", "react", "node", "database"],
    "IOT": ["embedded", "sensors", "arduino", "raspberry", "electronics"],
    "General": []
}

def get_working_days(start: date, end: date, public_holidays, fests):
    """Filter out weekends, holidays, and fests from a date range"""
    working_days = []
    current = start
    if current < date.today():
        current = date.today()
        
    while current <= end:
        # 1. Skip Weekends (5=Sat, 6=Sun)
        if current.weekday() < 5:
            # 2. Skip Public Holidays
            if current not in public_holidays:
                # 3. Skip University Fests
                if current.strftime("%Y-%m-%d") not in fests:
                    working_days.append(current)
        current += timedelta(days=1)
    return working_days

@router.get("/strategy/{username}")
async def get_strategic_roadmap(username: str):
    db = get_db()
    user = await db.users.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")

    # 1. Setup Date Context
    # In production, these come from a 'semester_config' collection
    sem_start = date(2026, 1, 1)
    sem_end = date(2026, 5, 30)
    today = date.today()
    
    # 2. Fetch External Blockers
    in_holidays = holidays.India(years=[2026])
    fest_docs = await db.events.find().to_list(None)
    fest_dates = [f["event_date"][:10] for f in fest_docs] # YYYY-MM-DD

    # 3. Calculate Math
    all_sem_working = get_working_days(sem_start, sem_end, in_holidays, fest_dates)
    remaining_working = get_working_days(today, sem_end, in_holidays, fest_dates)
    
    total_needed_count = math.ceil(0.75 * len(all_sem_working))
    current_attended = user.get("attended", 0)
    gap = max(0, total_needed_count - current_attended)
    
    # 4. Smart Logic Reasoning
    status_type = "SAFE"
    reasoning = ""
    if gap == 0:
        status_type = "SAFE"
        reasoning = f"Goal met! You are at {round((current_attended/len(all_sem_working))*100, 1)}%. You can safely skip mandatory classes, but check your Career Dates below."
    elif gap > len(remaining_working):
        status_type = "CRITICAL"
        reasoning = f"⚠️ CRITICAL RISK: It is impossible to hit 75%. You need {gap} classes but only {len(remaining_working)} remain. Please meet your counselor immediately."
    else:
        status_type = "ON_TRACK"
        reasoning = f"You need {gap} more classes. We have picked the best days for your {user.get('career_track', 'General')} track."

    # 5. Career-First Picker
    # Mocking subject-to-date mapping (In production, this joins with the timetable)
    p_dates = [] # Career Priority
    g_dates = [] # Buffer
    
    track = user.get("career_track", "General")
    keywords = CAREER_SUBJECT_MAP.get(track, [])
    
    # Simple logic: Every Tue/Thu is a "Career" day for this demo
    for d in remaining_working:
        if len(p_dates) + len(g_dates) >= gap + 5: break # Show gap + 5 buffer days
        
        if d.weekday() in [1, 3] and keywords: # Tue/Thu
            p_dates.append(d.strftime("%d-%m-%Y"))
        else:
            g_dates.append(d.strftime("%d-%m-%Y"))

    # Prioritize Career dates first to fill the gap
    final_p = p_dates[:gap] if len(p_dates) >= gap else p_dates
    final_g = g_dates[:(gap - len(final_p))] if gap > len(final_p) else g_dates[:5]

    return {
        "student_name": user.get("name"),
        "track": track,
        "stats": {
            "current_pct": round((current_attended/len(all_sem_working))*100, 1),
            "goal_pct": 75,
            "gap_number": gap,
            "days_remaining": len(remaining_working)
        },
        "message": {
            "type": status_type,
            "text": reasoning
        },
        "roadmap": {
            "career_priority": final_p,
            "buffer_attendance": final_g
        }
    }
