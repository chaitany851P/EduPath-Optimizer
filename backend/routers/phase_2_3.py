"""
Phase 2 & Phase 3 Routes - Exam Strategy & Academic Bridge
- Phase 2: End-Sem Diagnostic with "Double Danger Rule"
- Phase 3: Academic Bridge for prerequisite gap detection
"""

from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from models import (
    ExamStrategy,
    SubjectRiskDetails,
    RiskLevel,
    BridgeReport,
    PrerequisiteGap,
    AcademicPerformance,
)
from database import get_db

router = APIRouter()


def _serialize(doc):
    if doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


# ════════════════════════════════════════════════════════════════════════════════
# PHASE 2: END-SEMESTER EXAM STRATEGY (Double Danger Rule)
# ════════════════════════════════════════════════════════════════════════════════


@router.get("/exam-strategy/{student_id}", response_model=ExamStrategy)
async def get_exam_strategy(student_id: str):
    """
    Phase 2: End-Semester Diagnostic Strategy
    
    The "Double Danger Rule":
    - If Attendance < 75% AND Total Internals < 50%, mark as 'CRITICAL_RISK'
    - If either condition is met but not both, mark as 'WARNING'
    - Otherwise, mark as 'SAFE'
    
    Priority Score = (Missed Classes % * 0.5) + (Internal Marks Gap * 0.5)
    """
    db = get_db()
    
    # Fetch student
    student = await db.students.find_one({"student_id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Fetch all academic performance records for this student
    perf_records = []
    async for record in db.academic_performance.find({"student_id": student_id}):
        perf_records.append(_serialize(record))
    
    if not perf_records:
        raise HTTPException(
            status_code=404, detail="No academic performance records found for student"
        )
    
    # Fetch attendance data for all subjects taken by this student
    subject_codes = {r["subject_code"] for r in perf_records}
    
    prioritized_study_list = []
    critical_count = 0
    warning_count = 0
    safe_count = 0
    
    for subject_code in subject_codes:
        # Get performance record
        perf = next((r for r in perf_records if r["subject_code"] == subject_code), None)
        if not perf:
            continue
        
        # Get attendance summary
        total_classes = await db.attendance.count_documents(
            {"student_id": student_id, "subject_code": subject_code}
        )
        present_classes = await db.attendance.count_documents(
            {"student_id": student_id, "subject_code": subject_code, "status": "present"}
        )
        
        attendance_percentage = (
            round((present_classes / total_classes * 100), 2) if total_classes > 0 else 0
        )
        total_internal = perf.get("total_internal", 0)
        
        # Apply Double Danger Rule
        attendance_critical = attendance_percentage < 75
        marks_critical = total_internal < 50
        
        if attendance_critical and marks_critical:
            risk_level = RiskLevel.CRITICAL_RISK
            critical_count += 1
            message = "🚨 CRITICAL: Focus 70% of your revision time here due to low attendance and internals."
            revision_focus = "Complete review + Practice previous years exams"
        elif attendance_critical or marks_critical:
            risk_level = RiskLevel.WARNING
            warning_count += 1
            if attendance_critical:
                message = "⚠️ WARNING: Low attendance. Attend remaining classes and focus on exam preparation."
                revision_focus = "Attend all remaining classes + Target scoring well"
            else:
                message = "⚠️ WARNING: Low internal marks. Strong exam performance needed."
                revision_focus = "Deep concept review + Problem-solving practice"
        else:
            risk_level = RiskLevel.SAFE
            safe_count += 1
            message = "✓ SAFE: Maintain current level of preparation."
            revision_focus = "Regular revision + Optional advanced topics"
        
        # Calculate Priority Score
        missed_classes_percentage = 100 - attendance_percentage
        marks_gap = max(0, 50 - total_internal)  # How far below 50
        marks_gap_percentage = (marks_gap / 50) * 100
        
        priority_score = (missed_classes_percentage * 0.5) + (marks_gap_percentage * 0.5)
        
        subject_detail = SubjectRiskDetails(
            subject_code=subject_code,
            subject_name=perf.get("subject_name", subject_code),
            attendance_percentage=attendance_percentage,
            total_internal=total_internal,
            risk_level=risk_level,
            priority_score=priority_score,
            revision_focus=revision_focus,
            message=message,
        )
        prioritized_study_list.append(subject_detail)
    
    # Sort by priority score (highest first)
    prioritized_study_list.sort(key=lambda x: x.priority_score, reverse=True)
    
    # Determine overall status
    if critical_count > 0:
        overall_status = "🔴 CRITICAL: Urgent intervention needed"
    elif warning_count > 0:
        overall_status = "🟡 WARNING: Requires focused preparation"
    else:
        overall_status = "🟢 SAFE: On track to perform well"
    
    return ExamStrategy(
        student_id=student_id,
        total_risk_subjects=len(prioritized_study_list),
        critical_risk_count=critical_count,
        warning_count=warning_count,
        safe_count=safe_count,
        overall_status=overall_status,
        prioritized_study_list=prioritized_study_list,
    )


# ════════════════════════════════════════════════════════════════════════════════
# PHASE 3: ACADEMIC BRIDGE (Prerequisite Gap Detection)
# ════════════════════════════════════════════════════════════════════════════════


def _grade_from_marks(marks: float, max_marks: float = 50) -> str:
    """Convert marks to grade"""
    percentage = (marks / max_marks) * 100
    if percentage >= 90:
        return "A"
    elif percentage >= 80:
        return "B"
    elif percentage >= 70:
        return "C"
    elif percentage >= 60:
        return "D"
    else:
        return "F"


def _get_refresher_plan(prerequisite: str, weakness_percentage: float) -> List[str]:
    """Generate a 5-day refresher plan based on prerequisite and weakness severity"""
    refresher_plans = {
        "C Programming": [
            "Day 1: Review loops, arrays, and functions",
            "Day 2: Pointer concepts and memory management",
            "Day 3: Recursive functions and practice problems",
            "Day 4: Complex data structures in C",
            "Day 5: Mini-project combining all concepts",
        ],
        "Statistics": [
            "Day 1: Probability fundamentals and distributions",
            "Day 2: Mean, median, mode, and variance",
            "Day 3: Hypothesis testing basics",
            "Day 4: Correlation and regression",
            "Day 5: Real-world data analysis practice",
        ],
        "Mathematics": [
            "Day 1: Algebra and linear equations",
            "Day 2: Calculus basics (derivatives, integrals)",
            "Day 3: Matrices and linear algebra",
            "Day 4: Problem-solving techniques",
            "Day 5: Mock exams and practice",
        ],
        "Digital Electronics": [
            "Day 1: Logic gates and Boolean algebra",
            "Day 2: Combinational circuits",
            "Day 3: Sequential circuits and state machines",
            "Day 4: Flipflops and counters",
            "Day 5: Design project practice",
        ],
        "Data Structures": [
            "Day 1: Arrays, linked lists fundamentals",
            "Day 2: Stacks and queues",
            "Day 3: Trees and binary search trees",
            "Day 4: Graphs and traversal algorithms",
            "Day 5: Complexity analysis and optimization",
        ],
    }
    
    plan = refresher_plans.get(prerequisite, [
        "Day 1: Core concepts review",
        "Day 2: Important formulas and theorems",
        "Day 3: Practice problems from textbook",
        "Day 4: Previous exam papers",
        "Day 5: Full mock test and revision",
    ])
    
    return plan


def _calculate_gap_severity(prereq_marks: float, prereq_max: float = 50) -> str:
    """Calculate severity of prerequisite gap"""
    percentage = (prereq_marks / prereq_max) * 100
    if percentage < 40:
        return "CRITICAL"
    elif percentage < 50:
        return "HIGH"
    elif percentage < 65:
        return "MEDIUM"
    else:
        return "LOW"


@router.get("/bridge-report/{student_id}", response_model=BridgeReport)
async def get_bridge_report(student_id: str):
    """
    Phase 3: Academic Bridge Report
    
    Identifies gaps from previous semester and suggests refresher plans.
    Fetches the student's past semester grades and checks if current subjects
    depend on weak prerequisites.
    """
    db = get_db()
    
    # Fetch student
    student = await db.students.find_one({"student_id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student_semester = student.get("semester", 1)
    
    # Fetch all academic performance records
    all_perf_records = []
    async for record in db.academic_performance.find({"student_id": student_id}):
        all_perf_records.append(_serialize(record))
    
    if not all_perf_records:
        raise HTTPException(
            status_code=404, detail="No academic performance records found"
        )
    
    # Split into previous semester and current semester
    prev_semester_records = [
        r for r in all_perf_records if r.get("semester", 1) < student_semester
    ]
    current_semester_records = [
        r for r in all_perf_records if r.get("semester", 1) == student_semester
    ]
    
    if not prev_semester_records:
        # No previous semester data
        return BridgeReport(
            student_id=student_id,
            semester=student_semester,
            has_gaps=False,
            gap_count=0,
            prerequisites_failed=[],
            next_semester_recommendations=["You're in the first semester. Focus on building strong fundamentals!"],
        )
    
    # Get current subject codes
    current_subject_codes = {r["subject_code"] for r in current_semester_records}
    
    # Fetch curriculum mappings
    prerequisite_gaps = []
    
    # Group previous semester records by subject for faster lookup
    prev_perf_by_code = {r["subject_code"]: r for r in prev_semester_records}
    
    # Check all curriculum mappings to find current subjects with prerequisites
    async for mapping in db.curriculum_map.find():
        current_code = mapping.get("current_code")
        prereq_code = mapping.get("prerequisite_code")
        
        # If current subject is in student's current semester and prerequisite was in prev semester
        if current_code in current_subject_codes and prereq_code in prev_perf_by_code:
            prereq_perf = prev_perf_by_code[prereq_code]
            prereq_marks = prereq_perf.get("total_internal", 0)
            prereq_max = 50  # max possible marks for internal
            gap_severity = _calculate_gap_severity(prereq_marks, prereq_max)
            
            # Only flag as a gap if marks are below 65% (MEDIUM severity or worse)
            if gap_severity in ["CRITICAL", "HIGH", "MEDIUM"]:
                prereq_cie = prereq_perf.get("cie_marks", 0)
                prereq_grade = _grade_from_marks(prereq_marks, prereq_max)
                foundation_warning = (
                    f"Foundation Alert: Your performance in {mapping.get('prerequisite_subject')} "
                    f"({prereq_grade} grade) might make {mapping.get('current_subject')} challenging. "
                    f"Start your preparation early!"
                )
                
                gap = PrerequisiteGap(
                    prerequisite_subject=mapping.get("prerequisite_subject"),
                    prerequisite_grade=prereq_grade,
                    prerequisite_marks=prereq_marks,
                    current_subject=mapping.get("current_subject"),
                    gap_severity=gap_severity,
                    foundation_warning=foundation_warning,
                    refresher_plan=_get_refresher_plan(
                        mapping.get("prerequisite_subject"),
                        100 - ((prereq_marks / prereq_max) * 100),
                    ),
                )
                prerequisite_gaps.append(gap)
    
    # Generate recommendations
    recommendations = []
    if len(prerequisite_gaps) == 0:
        recommendations.append("✓ No prerequisite concerns. Continue with regular preparation.")
    else:
        recommendations.append("⚠️ Prerequisite gaps detected. Follow the refresher plans.")
        for gap in prerequisite_gaps:
            recommendations.append(
                f"Focus on {gap.prerequisite_subject} - severity: {gap.gap_severity}"
            )
        recommendations.append(
            "Schedule 5-10 hours in the first week to refresh weak prerequisites"
        )
    
    return BridgeReport(
        student_id=student_id,
        semester=student_semester,
        has_gaps=len(prerequisite_gaps) > 0,
        gap_count=len(prerequisite_gaps),
        prerequisites_failed=prerequisite_gaps,
        next_semester_recommendations=recommendations,
    )


@router.post("/academic-performance/", status_code=201)
async def add_academic_performance(performance: AcademicPerformance):
    """
    Add or update academic performance record for a student.
    Teacher endpoint for uploading marks.
    """
    db = get_db()
    
    # Verify student exists
    student = await db.students.find_one({"student_id": performance.student_id})
    if not student:
        raise HTTPException(
            status_code=404, detail=f"Student {performance.student_id} not found"
        )
    
    # Verify subject exists
    subject = await db.subjects.find_one({"subject_code": performance.subject_code})
    if not subject:
        raise HTTPException(
            status_code=404, detail=f"Subject {performance.subject_code} not found"
        )
    
    # Calculate total_internal if not provided
    data = performance.model_dump()
    data["total_internal"] = data.get("mid_term_marks", 0) + data.get("cie_marks", 0)
    data["last_updated"] = datetime.utcnow()
    
    # Upsert operation
    result = await db.academic_performance.update_one(
        {
            "student_id": performance.student_id,
            "subject_code": performance.subject_code,
        },
        {"$set": data},
        upsert=True,
    )
    
    return {
        "message": "Academic performance record saved successfully",
        "student_id": performance.student_id,
        "subject_code": performance.subject_code,
        "total_internal": data["total_internal"],
    }


@router.get("/academic-performance/{student_id}")
async def get_academic_performance(student_id: str):
    """Get all academic performance records for a student"""
    db = get_db()
    
    # Verify student exists
    student = await db.students.find_one({"student_id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    records = []
    async for record in db.academic_performance.find({"student_id": student_id}):
        records.append(_serialize(record))
    
    return {
        "student_id": student_id,
        "total_subjects": len(records),
        "records": records,
    }
