from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import date, timedelta, datetime
import holidays
import math

app = FastAPI(title="EduPath Optimizer - Core")

# --- MODELS (Best Practice for Data Validation) ---
class AttendanceInput(BaseModel):
    start_date: date
    end_date: date
    current_attended: int = Field(..., ge=0, description="Classes already attended")
    target_percentage: float = Field(default=75.0, ge=0, le=100)
    country_code: str = "IN"

# --- HELPER FUNCTIONS (Logic separated from API) ---
def get_working_days_list(start: date, end: date, country_code: str):
    """Calculates instructional days excluding weekends and public holidays."""
    if end < start:
        raise HTTPException(status_code=400, detail="End date cannot be before start date")
    
    # Load holidays for the specific years
    years = list(set([start.year, end.year]))
    all_holidays = holidays.CountryHoliday(country_code, years=years)
    
    instructional_days = []
    current = start
    while current <= end:
        # 0-4 are Mon-Fri, 5-6 are Sat/Sun
        if current.weekday() < 5 and current not in all_holidays:
            instructional_days.append(current)
        current += timedelta(days=1)
    return instructional_days, all_holidays

# --- ENDPOINTS (Updated Day 1, 2, 3) ---

@app.get("/")
def health_check():
    return {"status": "online", "version": "1.1", "updates": "Pydantic & Error Handling added"}

@app.post("/calculate-strategy")
def calculate_strategy(data: AttendanceInput):
    # 1. Get the list of actual class days
    working_days, holiday_list = get_working_days_list(data.start_date, data.end_date, data.country_code)
    total_working_count = len(working_days)
    
    # 2. Calculate targets
    required_total = math.ceil((data.target_percentage / 100) * total_working_count)
    gap = max(0, required_total - data.current_attended)
    
    # 3. Calculate "Days Left" from Today
    today = date.today()
    future_days = [d for d in working_days if d >= today]
    days_left = len(future_days)
    
    # 4. Verdict Logic
    if gap > days_left:
        verdict = "Impossible"
        advice = f"Critical: You need {gap} more days, but only {days_left} are left in the semester."
    elif gap == 0:
        verdict = "Safe"
        advice = "Excellent! You have already achieved your target attendance."
    else:
        verdict = "On Track"
        advice = f"You need to attend {gap} more classes out of the remaining {days_left} working days."

    return {
        "semester_summary": {
            "total_working_days": total_working_count,
            "public_holidays_skipped": len([h for h in holiday_list if data.start_date <= h <= data.end_date]),
            "target_classes_required": required_total
        },
        "student_status": {
            "current_attended": data.current_attended,
            "gap_to_fill": gap,
            "days_remaining_in_sem": days_left
        },
        "verdict": {
            "status": verdict,
            "advice": advice
        }
    }