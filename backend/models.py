from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import date
from enum import Enum


class CareerTrack(str, Enum):
    DATA_SCIENCE = "data_science"
    IOT = "iot"
    CYBER_SECURITY = "cyber_security"
    WEB_DEV = "web_development"
    AI_ML = "ai_ml"
    GENERAL = "general"


class Role(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    HOLIDAY = "holiday"
    UNIVERSITY_EVENT = "university_event"


# ---------- Student ----------
class StudentCreate(BaseModel):
    student_id: str
    name: str
    email: str
    branch: str
    semester: int
    career_track: CareerTrack = CareerTrack.GENERAL
    target_attendance: float = Field(default=75.0, ge=75.0, le=100.0)
    # Multi-Campus Support
    campus_id: str = Field(default="CAMPUS_001", description="Campus identifier")
    department_id: str = Field(default="DEPT_001", description="Department identifier")


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    career_track: Optional[CareerTrack] = None
    target_attendance: Optional[float] = Field(default=None, ge=75.0, le=100.0)


class Student(StudentCreate):
    id: Optional[str] = None

    class Config:
        from_attributes = True


# ---------- Subject ----------
class SubjectCreate(BaseModel):
    subject_code: str
    subject_name: str
    teacher_id: str
    career_tracks: List[CareerTrack] = []
    is_core: bool = False
    credits: int = 3
    total_classes_planned: int = 40
    # Multi-Campus Support
    campus_id: str = Field(default="CAMPUS_001", description="Campus identifier")
    department_id: str = Field(default="DEPT_001", description="Department identifier")


class Subject(SubjectCreate):
    id: Optional[str] = None

    class Config:
        from_attributes = True


# ---------- Attendance ----------
class AttendanceRecord(BaseModel):
    student_id: str
    subject_code: str
    date: date
    status: AttendanceStatus = AttendanceStatus.PRESENT


class AttendanceBulkUpdate(BaseModel):
    subject_code: str
    date: date
    student_statuses: Dict[str, AttendanceStatus]  # {student_id: status}


# ---------- Events ----------
class UniversityEvent(BaseModel):
    title: str
    event_date: date
    is_holiday: bool = False
    description: Optional[str] = None


# ---------- Optimization ----------
class OptimizationRequest(BaseModel):
    student_id: str
    semester_end_date: date
    upcoming_leave_dates: Optional[List[date]] = []


class DateClassification(BaseModel):
    date: date
    day_name: str
    subjects: List[str]
    classification: str  # "career_priority", "buffer", "holiday", "skip_safe"
    impact_score: float
    reason: str


class OptimizationResponse(BaseModel):
    student_id: str
    career_track: CareerTrack
    current_attendance: float
    target_attendance: float
    classes_attended: int
    total_classes_held: int
    classes_remaining: int
    min_classes_needed: int
    buffer_classes: int
    is_feasible: bool
    feasibility_message: str
    career_priority_dates: List[DateClassification]
    buffer_dates: List[DateClassification]
    skip_safe_dates: List[DateClassification]


# ---------- Phase 2: Academic Performance & Exam Strategy ----------
class RiskLevel(str, Enum):
    CRITICAL_RISK = "CRITICAL_RISK"
    WARNING = "WARNING"
    SAFE = "SAFE"


class AcademicPerformance(BaseModel):
    student_id: str
    subject_code: str
    subject_name: str
    mid_term_marks: float = Field(ge=0, le=30)  # out of 30
    cie_marks: float = Field(ge=0, le=20)  # out of 20
    total_internal: Optional[float] = None  # Sum of mid_term + cie
    # Multi-Campus Support
    campus_id: str = Field(default="CAMPUS_001", description="Campus identifier")
    department_id: str = Field(default="DEPT_001", description="Department identifier")

    class Config:
        from_attributes = True


class SubjectRiskDetails(BaseModel):
    subject_code: str
    subject_name: str
    attendance_percentage: float
    total_internal: float
    risk_level: RiskLevel
    priority_score: float
    revision_focus: str
    message: str


class ExamStrategy(BaseModel):
    student_id: str
    total_risk_subjects: int
    critical_risk_count: int
    warning_count: int
    safe_count: int
    overall_status: str
    prioritized_study_list: List[SubjectRiskDetails]


# ---------- Phase 3: Curriculum Mapping & Academic Bridge ----------
class CurriculumMapping(BaseModel):
    prerequisite_subject: str  # e.g., "C Programming"
    current_subject: str  # e.g., "Data Structures"
    semester_gap: int = 1  # How many semesters apart
    difficulty_multiplier: float = 1.0  # How much the gap matters

    class Config:
        from_attributes = True


class PrerequisiteGap(BaseModel):
    prerequisite_subject: str
    prerequisite_grade: str  # e.g., "D", "C", "B", "A"
    prerequisite_marks: float
    current_subject: str
    gap_severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    foundation_warning: str
    refresher_plan: List[str]  # 5-day refresher plan


class BridgeReport(BaseModel):
    student_id: str
    semester: int
    has_gaps: bool
    gap_count: int
    prerequisites_failed: List[PrerequisiteGap]
    next_semester_recommendations: List[str]
