from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
from database import get_db
import math

router = APIRouter()

def calculate_risk(att_pct, marks_val):
    # User's Logic: Safe (>80%, >70%), Warning (<75%, >60%), Critical (>80%, <40%), Double Danger (<70%, <40%)
    # Marks are out of 50 (30 Mid + 20 CIE)
    marks_pct = (marks_val / 50) * 100
    
    if att_pct > 80 and marks_pct > 70:
        return "SAFE", "Safe: Maintain regular revision.", "border-success"
    elif att_pct < 75 and marks_pct > 60:
        return "WARNING", "Warning: High marks but missed concepts due to low attendance.", "border-warning"
    elif att_pct > 80 and marks_pct < 40:
        return "CRITICAL", "Critical: Attended classes but failing to understand. Change study method.", "border-danger"
    elif att_pct < 70 and marks_pct < 40:
        return "DOUBLE DANGER", "🚨 DOUBLE DANGER: High probability of failing final exam.", "border-danger pulse-red"
    else:
        return "MODERATE", "Moderate risk: Balance attendance and study.", "border-info"

@router.get("/exam-strategy/{student_id}")
async def get_exam_strategy(student_id: str):
    db = get_db()
    # 1. Fetch Student & Performance
    student = await db.users.find_one({"username": student_id, "role": "student"})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    perf_records = await db.academic_performance.find({"student_id": student_id}).to_list(None)
    
    strategy_list = []
    total_stress = 0
    
    for record in perf_records:
        # Pull attendance for this specific subject (mocking 100 classes total for pct calculation)
        # In full system, this joins with the attendance collection
        att_pct = (student.get("attended", 15) / 20) * 100 # example math
        total_marks = record.get("total_internal", 0)
        
        # Stress Score = (MissedClasses% * 0.4) + (InternalMarksGap% * 0.6)
        missed_pct = 100 - att_pct
        marks_gap_pct = max(0, 50 - total_marks) / 50 * 100
        stress_score = (missed_pct * 0.4) + (marks_gap_pct * 0.6)
        
        level, msg, css = calculate_risk(att_pct, total_marks)
        
        strategy_list.append({
            "subject": record.get("subject_name"),
            "code": record.get("subject_code"),
            "attendance": round(att_pct, 1),
            "marks": total_marks,
            "risk_level": level,
            "message": msg,
            "css_class": css,
            "stress_score": round(stress_score, 2),
            "time_weight": 0 # calculated next
        })
        total_stress += stress_score

    # Calculate Time Allocation (Weightage)
    for s in strategy_list:
        if total_stress > 0:
            s["time_weight"] = round((s["stress_score"] / total_stress) * 100, 1)
        else:
            s["time_weight"] = round(100 / len(strategy_list), 1) if strategy_list else 0

    # Sort by Stress Score (Highest first)
    strategy_list.sort(key=lambda x: x["stress_score"], reverse=True)
    
    return {
        "overall_status": "CRITICAL" if any(s["risk_level"] == "DOUBLE DANGER" for s in strategy_list) else "STABLE",
        "prioritized_study_list": strategy_list,
        "counselor_alert": sum(1 for s in strategy_list if s["risk_level"] in ["CRITICAL", "DOUBLE DANGER"]) >= 3
    }
