from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from models import SubjectCreate, AttendanceBulkUpdate, AcademicPerformance
from pydantic import BaseModel, Field
from database import get_db
from datetime import date, datetime
import csv
import io

router = APIRouter()


class AttendanceUpdate(BaseModel):
    student_id: str
    attended_count: int = Field(..., ge=0)


def _serialize(doc):
    if doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


@router.get("/students")
async def list_students_teacher():
    """List all students for teacher dashboard"""
    db = get_db()
    students = []
    async for u in db.users.find({"role": "student"}, {"_id": 0, "password_hash": 0}):
        students.append(u)
    return {"students": students}


@router.post("/update-attendance")
async def update_attendance_single(data: AttendanceUpdate):
    """Update attendance for a single student (Legacy support)"""
    db = get_db()
    result = await db.users.update_one(
        {"username": data.student_id},
        {"$set": {"attended": data.attended_count}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": f"Attendance updated for {data.student_id}"}


@router.post("/subjects/", status_code=201)
async def create_subject(subject: SubjectCreate):
    db = get_db()
    existing = await db.subjects.find_one({"subject_code": subject.subject_code})
    if existing:
        raise HTTPException(status_code=400, detail="Subject code already exists")
    result = await db.subjects.insert_one(subject.model_dump())
    return {"id": str(result.inserted_id), "message": "Subject created successfully"}


@router.get("/subjects/")
async def list_subjects():
    db = get_db()
    subjects = []
    async for s in db.subjects.find():
        subjects.append(_serialize(s))
    return subjects


@router.get("/subjects/{subject_code}")
async def get_subject(subject_code: str):
    db = get_db()
    subject = await db.subjects.find_one({"subject_code": subject_code})
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return _serialize(subject)


@router.post("/attendance/bulk")
async def bulk_update_attendance(update: AttendanceBulkUpdate):
    db = get_db()
    ops = []
    for student_id, status in update.student_statuses.items():
        record = {
            "student_id": student_id,
            "subject_code": update.subject_code,
            "date": update.date.isoformat(),
            "status": status.value,
        }
        ops.append(record)
    if ops:
        await db.attendance.insert_many(ops)
    return {"message": f"Attendance recorded for {len(ops)} students"}


@router.get("/attendance/{subject_code}/{date_str}")
async def get_attendance_by_date(subject_code: str, date_str: str):
    db = get_db()
    records = []
    async for r in db.attendance.find({"subject_code": subject_code, "date": date_str}):
        records.append(_serialize(r))
    return records


# ════════════════════════════════════════════════════════════════════════════════
# PHASE 2-3: TEACHER MARKS UPLOAD
# ════════════════════════════════════════════════════════════════════════════════

@router.post("/upload-marks/csv")
async def upload_marks_csv(subject_code: str, file: UploadFile = File(...)):
    """
    Upload student marks via CSV file.
    
    Expected CSV format:
    student_id,subject_code,subject_name,mid_term_marks,cie_marks
    2024001,CS101,C Programming,18,15
    2024002,CS101,C Programming,25,19
    ...
    
    mid_term_marks: 0-30
    cie_marks: 0-20
    total_internal: sum of both (0-50)
    """
    db = get_db()
    
    try:
        # Verify subject exists
        subject = await db.subjects.find_one({"subject_code": subject_code})
        if not subject:
            raise HTTPException(status_code=404, detail=f"Subject {subject_code} not found")
        
        # Read CSV file
        content = await file.read()
        csv_reader = csv.DictReader(io.StringIO(content.decode('utf-8')))
        
        records_inserted = []
        errors = []
        row_idx = 1
        
        for row_idx, row in enumerate(csv_reader, start=2):  # Start at 2 (row 1 is header)
            try:
                student_id = row.get('student_id', '').strip()
                mid_term = float(row.get('mid_term_marks', 0))
                cie = float(row.get('cie_marks', 0))
                subject_name = row.get('subject_name', subject['subject_name']).strip()
                
                # Validate
                if not student_id:
                    errors.append(f"Row {row_idx}: Missing student_id")
                    continue
                if not (0 <= mid_term <= 30):
                    errors.append(f"Row {row_idx}: mid_term_marks must be 0-30 (got {mid_term})")
                    continue
                if not (0 <= cie <= 20):
                    errors.append(f"Row {row_idx}: cie_marks must be 0-20 (got {cie})")
                    continue
                
                # Verify student exists
                student = await db.students.find_one({"student_id": student_id})
                if not student:
                    errors.append(f"Row {row_idx}: Student {student_id} not found in system")
                    continue
                
                # Create or update performance record
                total_internal = mid_term + cie
                data = {
                    "student_id": student_id,
                    "subject_code": subject_code,
                    "subject_name": subject_name,
                    "mid_term_marks": mid_term,
                    "cie_marks": cie,
                    "total_internal": total_internal,
                    "semester": student.get("semester", 1),
                    "uploaded_by_teacher": subject['teacher_id'],
                    "upload_date": datetime.utcnow(),
                }
                
                result = await db.academic_performance.update_one(
                    {
                        "student_id": student_id,
                        "subject_code": subject_code,
                    },
                    {"$set": data},
                    upsert=True,
                )
                
                records_inserted.append({
                    "student_id": student_id,
                    "total_internal": total_internal,
                    "status": "inserted" if result.upserted_id else "updated"
                })
                
            except ValueError as e:
                errors.append(f"Row {row_idx}: Invalid numeric value - {str(e)}")
            except Exception as e:
                errors.append(f"Row {row_idx}: {str(e)}")
        
        # Save upload metadata
        upload_record = {
            "teacher_id": subject['teacher_id'],
            "subject_code": subject_code,
            "file_name": file.filename,
            "total_rows": row_idx - 1 if row_idx > 1 else 0,
            "successful_uploads": len(records_inserted),
            "errors": len(errors),
            "upload_date": datetime.utcnow(),
            "error_details": errors[:10],  # Store first 10 errors
        }
        await db.mark_uploads.insert_one(upload_record)
        
        return {
            "message": "Marks uploaded successfully",
            "file": file.filename,
            "total_records": row_idx - 1 if row_idx > 1 else 0,
            "successful": len(records_inserted),
            "failed": len(errors),
            "errors": errors[:10],  # Return first 10 errors to user
            "inserted_records": records_inserted[:20],  # Show first 20 inserted
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")


@router.post("/upload-marks/bulk")
async def upload_marks_bulk(marks: list):
    """
    Upload multiple student marks as JSON payload.
    
    Payload format:
    [
      {
        "student_id": "2024001",
        "subject_code": "CS101",
        "subject_name": "C Programming",
        "mid_term_marks": 18,
        "cie_marks": 15
      },
      ...
    ]
    """
    db = get_db()
    
    if not marks:
        raise HTTPException(status_code=400, detail="No marks provided")
    
    records_inserted = []
    errors = []
    
    for idx, mark_entry in enumerate(marks):
        try:
            student_id = mark_entry.get('student_id', '').strip()
            subject_code = mark_entry.get('subject_code', '').strip()
            mid_term = float(mark_entry.get('mid_term_marks', 0))
            cie = float(mark_entry.get('cie_marks', 0))
            subject_name = mark_entry.get('subject_name', '').strip()
            
            # Validate
            if not student_id or not subject_code:
                errors.append(f"Entry {idx + 1}: Missing student_id or subject_code")
                continue
            if not (0 <= mid_term <= 30):
                errors.append(f"Entry {idx + 1}: mid_term_marks must be 0-30")
                continue
            if not (0 <= cie <= 20):
                errors.append(f"Entry {idx + 1}: cie_marks must be 0-20")
                continue
            
            # Verify student and subject
            student = await db.students.find_one({"student_id": student_id})
            subject = await db.subjects.find_one({"subject_code": subject_code})
            
            if not student:
                errors.append(f"Entry {idx + 1}: Student {student_id} not found")
                continue
            if not subject:
                errors.append(f"Entry {idx + 1}: Subject {subject_code} not found")
                continue
            
            # Create or update
            total_internal = mid_term + cie
            data = {
                "student_id": student_id,
                "subject_code": subject_code,
                "subject_name": subject_name or subject['subject_name'],
                "mid_term_marks": mid_term,
                "cie_marks": cie,
                "total_internal": total_internal,
                "semester": student.get("semester", 1),
                "uploaded_by_teacher": subject['teacher_id'],
                "upload_date": datetime.utcnow(),
            }
            
            result = await db.academic_performance.update_one(
                {
                    "student_id": student_id,
                    "subject_code": subject_code,
                },
                {"$set": data},
                upsert=True,
            )
            
            records_inserted.append({
                "student_id": student_id,
                "subject_code": subject_code,
                "total_internal": total_internal,
                "status": "inserted" if result.upserted_id else "updated"
            })
            
        except ValueError:
            errors.append(f"Entry {idx + 1}: Invalid numeric values")
        except Exception as e:
            errors.append(f"Entry {idx + 1}: {str(e)}")
    
    if len(records_inserted) == 0:
        raise HTTPException(status_code=400, detail=f"No valid records to insert. Errors: {errors}")
    
    return {
        "message": "Marks uploaded successfully",
        "total_entries": len(marks),
        "successful": len(records_inserted),
        "failed": len(errors),
        "errors": errors[:10],
        "inserted_records": records_inserted,
    }


@router.get("/upload-history/{subject_code}")
async def get_upload_history(subject_code: str):
    """Get history of mark uploads for a subject"""
    db = get_db()
    
    # Verify subject
    subject = await db.subjects.find_one({"subject_code": subject_code})
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    uploads = []
    async for upload in db.mark_uploads.find(
        {"subject_code": subject_code}
    ).sort("upload_date", -1).limit(20):
        uploads.append(_serialize(upload))
    
    return {
        "subject_code": subject_code,
        "total_uploads": len(uploads),
        "recent_uploads": uploads,
    }
