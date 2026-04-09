# EduPath Optimizer - Phase 2 & 3 Implementation Guide

## 🎯 Overview

This document covers the implementation of **Phase 2 (End-Semester Exam Strategy)** and **Phase 3 (Academic Bridge)** for the EduPath Optimizer system.

---

## 📦 What's New

### Phase 2: Final Exam Readiness 📚
- **Double Danger Rule**: Identifies critical risk subjects where Both attendance < 75% AND internals < 50%
- **Priority Score**: Calculates revision urgency based on attendance gaps and internal marks
- **Personalized Study List**: Ranked by priority with specific revision strategies
- **Color-Coded Dashboard**: Red (Critical), Yellow (Warning), Green (Safe)

### Phase 3: New Semester Foundation Check 🌉
- **Prerequisite Gap Detection**: Identifies weak subjects from previous semesters
- **5-Day Refresher Plans**: Custom learning paths for each prerequisite
- **Foundation Warnings**: Alerts when weak prerequisites affect new subjects
- **Semester-to-Semester Bridge**: Tracks academic progression and dependencies

### Teacher Features 👨‍🏫
- **Marks Upload (CSV & JSON)**: Easy import of student marks
- **Upload History**: Track all mark uploads per subject
- **Data Validation**: Automatic error checking and reporting

---

## 🗄️ Database Structure

### New Collections

#### `academic_performance`
```javascript
{
  "_id": ObjectId,
  "student_id": "2024001",
  "subject_code": "CS101",
  "subject_name": "C Programming",
  "mid_term_marks": 18,          // 0-30
  "cie_marks": 15,               // 0-20
  "total_internal": 33,          // sum of above
  "semester": 1,
  "uploaded_by_teacher": "T001",
  "upload_date": ISODate
}
```

Indexes:
- `student_id + subject_code` (for quick lookups per student/subject)

#### `curriculum_map`
```javascript
{
  "_id": ObjectId,
  "prerequisite_subject": "C Programming",
  "prerequisite_code": "CS101",
  "current_subject": "Data Structures",
  "current_code": "DS101",
  "semester_gap": 1,
  "difficulty_multiplier": 1.2,
  "description": "Data Structures builds on C Programming fundamentals"
}
```

Indexes:
- `prerequisite_code + current_code`

#### `mark_uploads` (tracking)
```javascript
{
  "_id": ObjectId,
  "teacher_id": "T001",
  "subject_code": "CS101",
  "file_name": "marks_cs101_2024.csv",
  "total_rows": 60,
  "successful_uploads": 58,
  "errors": 2,
  "upload_date": ISODate,
  "error_details": [...]
}
```

---

## 🚀 Getting Started

### 1. Seed Initial Data

```bash
cd e:\SGP\EduPath_Optimizer
python seed_phase2_3.py
```

This creates:
- ✓ 10 academic performance records across 3 test students
- ✓ 6 curriculum mappings (prerequisite chains)
- ✓ Test data with intentional gaps for debugging

**Test Students Created:**
- `2024001`: Mixed performance (CRITICAL in Machine Learning, GOOD in C Programming)
- `2024002`: Strong performer (all subjects 80%+)
- `2024003`: Weak in Digital Electronics (testing prerequisite chain)

---

## 🔌 API Endpoints

### Phase 2: Exam Strategy

#### GET `/api/phase-2-3/exam-strategy/{student_id}`

Returns comprehensive exam readiness analysis with the "Double Danger Rule"

**Response:**
```json
{
  "student_id": "2024001",
  "total_risk_subjects": 5,
  "critical_risk_count": 1,
  "warning_count": 2,
  "safe_count": 2,
  "overall_status": "🟡 WARNING: Requires focused preparation",
  "prioritized_study_list": [
    {
      "subject_code": "ML101",
      "subject_name": "Machine Learning",
      "attendance_percentage": 60.5,
      "total_internal": 15.0,
      "risk_level": "CRITICAL_RISK",
      "priority_score": 42.75,
      "revision_focus": "Complete review + Practice previous years exams",
      "message": "🚨 CRITICAL: Focus 70% of your revision time here due to low attendance and internals."
    },
    ...
  ]
}
```

#### Priority Score Formula
```
Priority Score = (Missed Classes % × 0.5) + (Internal Marks Gap % × 0.5)
```
- Higher score = Higher revision priority
- Missed Classes % = 100 - Attendance %
- Marks Gap % = max(0, (50 - Total Internal) / 50) × 100

---

### Phase 3: Academic Bridge

#### GET `/api/phase-2-3/bridge-report/{student_id}`

Identifies prerequisite gaps and generates refresher plans

**Response:**
```json
{
  "student_id": "2024001",
  "semester": 2,
  "has_gaps": true,
  "gap_count": 2,
  "prerequisites_failed": [
    {
      "prerequisite_subject": "Statistics",
      "prerequisite_grade": "D",
      "prerequisite_marks": 19.0,
      "current_subject": "Machine Learning",
      "gap_severity": "HIGH",
      "foundation_warning": "Foundation Alert: Your performance in Statistics (D grade) last sem might make Machine Learning difficult. Start early!",
      "refresher_plan": [
        "Day 1: Probability fundamentals and distributions",
        "Day 2: Mean, median, mode, and variance",
        "Day 3: Hypothesis testing basics",
        "Day 4: Correlation and regression",
        "Day 5: Real-world data analysis practice"
      ]
    }
  ],
  "next_semester_recommendations": [
    "⚠️ Prerequisite gaps detected. Follow the refresher plans.",
    "Focus on Statistics - severity: HIGH",
    "Schedule 5-10 hours in the first week to refresh weak prerequisites"
  ]
}
```

#### Gap Severity Levels
```
- CRITICAL: Marks < 40% (failing)
- HIGH: Marks 40-50% (weak)
- MEDIUM: Marks 50-65% (below average)
- LOW: Marks 65%+ (acceptable)
```

---

### Academic Performance Management

#### POST `/api/phase-2-3/academic-performance/`

Add or update a student's marks for a subject

```json
{
  "student_id": "2024001",
  "subject_code": "CS101",
  "subject_name": "C Programming",
  "mid_term_marks": 18,
  "cie_marks": 15
}
```

#### GET `/api/phase-2-3/academic-performance/{student_id}`

Get all academic performance records for a student

**Response:**
```json
{
  "student_id": "2024001",
  "total_subjects": 5,
  "records": [...]
}
```

---

### Teacher: Marks Upload

#### POST `/api/teachers/upload-marks/csv`

Upload marks via CSV file

**Parameters:**
- `subject_code` (query): Subject code for all records
- `file` (multipart): CSV file

**CSV Format:**
```csv
student_id,subject_code,subject_name,mid_term_marks,cie_marks
2024001,CS101,C Programming,18,15
2024002,CS101,C Programming,25,19
2024003,CS101,C Programming,22,17
```

**Response:**
```json
{
  "message": "Marks uploaded successfully",
  "file": "marks.csv",
  "total_records": 60,
  "successful": 58,
  "failed": 2,
  "errors": [
    "Row 15: mid_term_marks must be 0-30 (got 35)",
    "Row 42: Student 2024999 not found in system"
  ],
  "inserted_records": [...]
}
```

#### POST `/api/teachers/upload-marks/bulk`

Upload marks via JSON payload

```json
[
  {
    "student_id": "2024001",
    "subject_code": "CS101",
    "subject_name": "C Programming",
    "mid_term_marks": 18,
    "cie_marks": 15
  },
  {
    "student_id": "2024002",
    "subject_code": "CS101",
    "subject_name": "C Programming",
    "mid_term_marks": 25,
    "cie_marks": 19
  }
]
```

#### GET `/api/teachers/upload-history/{subject_code}`

View all upload history for a subject

---

## 🎨 Student Dashboard

### New Dashboard Sections

#### 📚 Tab: Final Exam Readiness
Shows:
- Overall exam status (CRITICAL / WARNING / SAFE)
- 4-stat card grid (Critical Risk count, Warning count, Safe count, Total subjects)
- Color-coded priority table with:
  - Subject name
  - Attendance percentage
  - Internal marks out of 50
  - Risk level badge
  - Revision focus strategy
- "Double Danger Rule" explanation card

#### 🌉 Tab: New Semester Foundation Check
Shows:
- Foundation gap alerts at top
- 4-stat card grid (Total gaps, Critical count, High count, Current semester)
- Prerequisites with gaps (if any):
  - Prerequisite → Current Subject mapping
  - Grade and marks from previous semester
  - Gap severity badge
  - 5-day refresher plan
- Recommendations and action items

---

## 📊 Key Logic Patterns

### The "Double Danger Rule" (Phase 2)

```python
if attendance < 75% AND total_internal < 50:
    risk_level = "CRITICAL_RISK"
    revision_focus = "70% of time here"
elif attendance < 75% OR total_internal < 50:
    risk_level = "WARNING"
    revision_focus = "Targeted preparation"
else:
    risk_level = "SAFE"
    revision_focus = "Regular revision"
```

### Prerequisite Chain Matching (Phase 3)

1. Get all subjects student took in previous semester
2. Get all subjects in current semester
3. For each prerequisite mapping:
   - If prerequisite was in previous semester AND current subject is in current semester
   - Calculate grade from previous marks
   - If grade indicates weakness (< 65%), flag as gap
   - Generate 5-day refresher plan

### Refresher Plans

Predefined 5-day plans for:
- C Programming
- Statistics
- Mathematics
- Digital Electronics
- Data Structures
- (Extensible for new subjects)

---

## 🔧 Integration Checklist

- [x] Database models updated
- [x] Phase 2 backend logic implemented
- [x] Phase 3 backend logic implemented
- [x] Teacher marks upload endpoint
- [x] Student dashboard UI sections
- [x] Seed script with test data
- [x] API documentation
- [ ] Email notifications for CRITICAL risks
- [ ] Counselor dashboard view
- [ ] Mobile app sync
- [ ] Export to PDF

---

## 🐛 Testing Workflow

### 1. Seed Test Data
```bash
python seed_phase2_3.py
```

### 2. Test Phase 2 Endpoint
```bash
curl -X GET "http://localhost:8000/api/phase-2-3/exam-strategy/2024001" \
  -H "Authorization: Bearer {token}"
```

Expected: CRITICAL RISK for ML101, WARNING for others

### 3. Test Phase 3 Endpoint
```bash
curl -X GET "http://localhost:8000/api/phase-2-3/bridge-report/2024001" \
  -H "Authorization: Bearer {token}"
```

Expected: High gap in Statistics → Machine Learning link

### 4. Test Teacher Upload
```bash
curl -X POST "http://localhost:8000/api/teachers/upload-marks/csv?subject_code=CS101" \
  -F "file=@marks.csv" \
  -H "Authorization: Bearer {teacher_token}"
```

---

## 📝 CSV Upload Template

Save as `marks.csv`:

```csv
student_id,subject_code,subject_name,mid_term_marks,cie_marks
2024001,CS101,C Programming,18,15
2024002,CS101,C Programming,25,19
2024003,CS101,C Programming,22,17
2024004,CS101,C Programming,28,20
2024005,CS101,C Programming,14,11
```

**Important:**
- `mid_term_marks`: Must be 0-30
- `cie_marks`: Must be 0-20
- `subject_code`: Must match a subject in the system
- `student_id`: Must match a student in the system

---

## 🔐 Permissions & Access

### Student Permissions
- View own exam strategy: `GET /api/phase-2-3/exam-strategy/{self}`
- View own bridge report: `GET /api/phase-2-3/bridge-report/{self}`
- View own performance: `GET /api/phase-2-3/academic-performance/{self}`

### Teacher Permissions
- Upload marks for their subjects: `POST /api/teachers/upload-marks/*`
- View upload history: `GET /api/teachers/upload-history/{their_subject}`

### Admin Permissions
- All endpoints (view all data, manage all uploads)

---

## 🚨 Error Handling

### Common CSV Upload Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `mid_term_marks must be 0-30 (got 35)` | Out of range | Ensure marks ≤ 30 |
| `Student 2024999 not found` | Invalid ID | Check student exists in system |
| `Subject CS101 not found` | Invalid code | Use correct subject code |
| `Invalid numeric value` | Non-number in marks column | Use numbers only |

---

## 📌 Best Practices

1. **Seed Data First**: Always run seed script before testing
2. **Validate Before Upload**: Check CSV format before bulk upload
3. **Monitor Critical Risks**: Implement notifications for CRITICAL_RISK students
4. **Track Improvements**: Compare marks across semesters
5. **Use Refresher Plans**: Encourage students to follow 5-day plans
6. **Regular Updates**: Keep curriculum_map current with prerequisite changes

---

## 🔄 Updating Prerequisite Maps

Add new prerequisite mapping:

```javascript
db.curriculum_map.insertOne({
  prerequisite_subject: "Your Subject",
  prerequisite_code: "YOURCODE",
  current_subject: "Dependent Subject",
  current_code: "DEPCODE",
  semester_gap: 1,
  difficulty_multiplier: 1.2,
  description: "Why this prerequisite matters"
})
```

Update refresher plan for new subject (in `phase_2_3.py`):

```python
def _get_refresher_plan(prerequisite: str, weakness_percentage: float):
    refresher_plans = {
        ...
        "Your Subject": [
            "Day 1: Topic A",
            "Day 2: Topic B",
            ...
        ]
    }
```

---

## 📞 Support

For questions on:
- **Phase 2 Logic**: Check "Double Danger Rule" section
- **Phase 3 Prerequisites**: Check curriculum_map in MongoDB
- **API Errors**: Check response status and error detail
- **CSV Upload Issues**: Validate format against template

---

## 📅 Version History

- **v2.0.0** - Phase 2 & 3 implementation (April 2026)
- **v1.0.0** - Phase 1: Attendance optimization (Initial release)

---

**Done! Your EduPath Optimizer now supports Phase 2 and Phase 3 workflows.** 🎓
