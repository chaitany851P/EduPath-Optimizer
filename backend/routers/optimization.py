from fastapi import APIRouter, HTTPException
from models import OptimizationRequest, OptimizationResponse, DateClassification, CareerTrack
from database import get_db
from datetime import date, timedelta
import math
import holidays

router = APIRouter()

# Career track → high-priority subject keywords
CAREER_SUBJECT_MAP = {
    CareerTrack.DATA_SCIENCE: ["python", "ml", "machine learning", "statistics", "data", "analytics", "r programming"],
    CareerTrack.IOT: ["embedded", "iot", "microcontroller", "arduino", "raspberry", "sensors", "networking"],
    CareerTrack.CYBER_SECURITY: ["security", "cryptography", "network security", "ethical hacking", "firewall", "cyber"],
    CareerTrack.WEB_DEV: ["web", "html", "css", "javascript", "react", "node", "database", "api"],
    CareerTrack.AI_ML: ["ai", "neural", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch"],
    CareerTrack.GENERAL: [],
}


def get_india_holidays(year: int):
    try:
        return holidays.India(years=year)
    except Exception:
        return {}


def is_weekend(d: date) -> bool:
    return d.weekday() >= 5  # Saturday=5, Sunday=6


def get_instructional_days(start: date, end: date, university_events: list) -> list:
    """Return all weekdays between start/end that are not holidays or uni events."""
    india_holidays = get_india_holidays(start.year)
    if start.year != end.year:
        india_holidays.update(get_india_holidays(end.year))

    event_dates = {date.fromisoformat(e["event_date"]) for e in university_events if e.get("is_holiday")}

    days = []
    current = start
    while current <= end:
        if not is_weekend(current) and current not in india_holidays and current not in event_dates:
            days.append(current)
        current += timedelta(days=1)
    return days


def subject_matches_career(subject_name: str, subject_code: str, career_track: CareerTrack) -> bool:
    keywords = CAREER_SUBJECT_MAP.get(career_track, [])
    combined = (subject_name + " " + subject_code).lower()
    return any(kw in combined for kw in keywords)


def calculate_impact_score(subjects_on_day: list, career_track: CareerTrack, is_core_day: bool) -> float:
    """Score 0–10 based on career relevance."""
    if not subjects_on_day:
        return 0.0
    career_matches = sum(
        1 for s in subjects_on_day if subject_matches_career(s.get("subject_name", ""), s.get("subject_code", ""), career_track)
    )
    core_count = sum(1 for s in subjects_on_day if s.get("is_core", False))
    score = (career_matches / len(subjects_on_day)) * 6 + (core_count / len(subjects_on_day)) * 4
    return round(score, 2)


@router.post("/", response_model=OptimizationResponse)
async def optimize_attendance(req: OptimizationRequest):
    db = get_db()

    # Fetch student
    student = await db.students.find_one({"student_id": req.student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    career_track = CareerTrack(student.get("career_track", "general"))
    target_pct = student.get("target_attendance", 75.0)

    # Fetch all subjects
    subjects_list = []
    async for s in db.subjects.find():
        subjects_list.append(s)

    # Fetch attendance records
    attended = 0
    total_held = 0
    async for r in db.attendance.find({"student_id": req.student_id}):
        total_held += 1
        if r.get("status") == "present":
            attended += 1

    current_pct = round((attended / total_held * 100), 2) if total_held > 0 else 0.0

    # Fetch university events
    events = []
    async for e in db.events.find():
        events.append(e)

    # Get semester config
    config = await db.config.find_one({"key": "semester"})
    semester_start = date.today()
    if config:
        try:
            semester_start = date.fromisoformat(config.get("start_date", date.today().isoformat()))
        except Exception:
            pass

    # Get remaining instructional days
    remaining_days = get_instructional_days(date.today(), req.semester_end_date, events)

    # Remove requested leave dates
    leave_set = set(req.upcoming_leave_dates or [])
    remaining_days = [d for d in remaining_days if d not in leave_set]

    classes_remaining = len(remaining_days)
    total_projected = total_held + classes_remaining

    # Minimum classes needed: math.ceil((target/100) * total_projected) - attended
    min_needed = math.ceil((target_pct / 100) * total_projected) - attended
    min_needed = max(0, min_needed)

    buffer = classes_remaining - min_needed
    is_feasible = min_needed <= classes_remaining

    if not is_feasible:
        msg = (
            f"⚠️ It is mathematically impossible to reach {target_pct}% attendance. "
            f"You need {min_needed} more classes but only {classes_remaining} remain. "
            "Please meet your counselor."
        )
    elif buffer == 0:
        msg = f"⚠️ You must attend EVERY remaining class to reach {target_pct}%. No buffer left."
    elif buffer <= 3:
        msg = f"⚠️ You can only afford to skip {buffer} more class(es). Be strategic."
    else:
        msg = f"✅ You have a buffer of {buffer} class(es) you can strategically skip while maintaining {target_pct}%."

    # Build daily classification
    india_holidays_map = get_india_holidays(date.today().year)
    event_dates = {date.fromisoformat(e["event_date"]): e for e in events}

    career_priority = []
    buffer_dates_list = []
    skip_safe_list = []

    for d in remaining_days:
        day_name = d.strftime("%A, %d %b %Y")
        # Identify subjects on this weekday (simplified: all subjects round-robin by weekday)
        day_subjects = [s for s in subjects_list if (d.weekday() % max(len(subjects_list), 1)) == subjects_list.index(s) % 5]
        if not day_subjects:
            day_subjects = subjects_list[:2] if len(subjects_list) >= 2 else subjects_list

        impact = calculate_impact_score(day_subjects, career_track, any(s.get("is_core") for s in day_subjects))
        subject_names = [s.get("subject_name", s.get("subject_code", "Unknown")) for s in day_subjects]

        if impact >= 6.0:
            classification = "career_priority"
            reason = f"High-impact day for {career_track.value.replace('_', ' ').title()} track"
            career_priority.append(DateClassification(
                date=d, day_name=day_name, subjects=subject_names,
                classification=classification, impact_score=impact, reason=reason
            ))
        elif impact >= 3.0 or min_needed > 0:
            classification = "buffer"
            reason = "Required for 75% threshold — attend to maintain compliance"
            min_needed = max(0, min_needed - 1)
            buffer_dates_list.append(DateClassification(
                date=d, day_name=day_name, subjects=subject_names,
                classification=classification, impact_score=impact, reason=reason
            ))
        else:
            classification = "skip_safe"
            reason = "Low career impact — safe to skip if buffer allows"
            skip_safe_list.append(DateClassification(
                date=d, day_name=day_name, subjects=subject_names,
                classification=classification, impact_score=impact, reason=reason
            ))

    return OptimizationResponse(
        student_id=req.student_id,
        career_track=career_track,
        current_attendance=current_pct,
        target_attendance=target_pct,
        classes_attended=attended,
        total_classes_held=total_held,
        classes_remaining=classes_remaining,
        min_classes_needed=buffer,
        buffer_classes=buffer,
        is_feasible=is_feasible,
        feasibility_message=msg,
        career_priority_dates=career_priority,
        buffer_dates=buffer_dates_list,
        skip_safe_dates=skip_safe_list,
    )


@router.get("/summary/{student_id}")
async def get_quick_summary(student_id: str):
    """Quick stats without full optimization."""
    db = get_db()
    student = await db.students.find_one({"student_id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    attended = 0
    total = 0
    async for r in db.attendance.find({"student_id": student_id}):
        total += 1
        if r.get("status") == "present":
            attended += 1

    pct = round((attended / total * 100), 2) if total > 0 else 0.0
    target = student.get("target_attendance", 75.0)

    return {
        "student_id": student_id,
        "name": student.get("name"),
        "career_track": student.get("career_track"),
        "current_attendance": pct,
        "target_attendance": target,
        "classes_attended": attended,
        "total_classes": total,
        "status": "safe" if pct >= target else "at_risk" if pct >= target - 5 else "critical",
    }
