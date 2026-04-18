import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "edupath_db")

async def seed_presentation_data():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("🎬 Seeding Rich Presentation Data (Phase 2 & 3)...")
    
    # 1. Clear existing collections
    await db.academic_performance.delete_many({})
    await db.curriculum_map.delete_many({})
    await db.subjects.delete_many({})
    
    # 2. Add Comprehensive Subjects
    subjects = [
        {"subject_code": "CS101", "subject_name": "Data Structures"},
        {"subject_code": "CS102", "subject_name": "Database Management"},
        {"subject_code": "CS103", "subject_name": "Python Programming"},
        {"subject_code": "CS104", "subject_name": "Mathematics II"},
        {"subject_code": "CS091", "subject_name": "C Programming (Sem 1)"},
        {"subject_code": "CS092", "subject_name": "Mathematics I (Sem 1)"}
    ]
    await db.subjects.insert_many(subjects)

    # 3. Add Curriculum Mappings (Phase 3 Bridge)
    curriculum = [
        {
            "current_code": "CS101", "current_subject": "Data Structures",
            "prerequisite_code": "CS091", "prerequisite_subject": "C Programming"
        },
        {
            "current_code": "CS104", "current_subject": "Mathematics II",
            "prerequisite_code": "CS092", "prerequisite_subject": "Mathematics I"
        }
    ]
    await db.curriculum_map.insert_many(curriculum)

    # 4. Create Performance Records for Student 1 (Rajesh - CRITICAL)
    # Goal: Show critical risk in CS101 and a Bridge Gap in CS101 due to poor Sem 1 C Programming
    rajesh_perf = [
        # Current Semester (Sem 2)
        {"student_id": "2024001", "subject_code": "CS101", "subject_name": "Data Structures", "mid_term_marks": 8, "cie_marks": 10, "total_internal": 18, "semester": 2},
        {"student_id": "2024001", "subject_code": "CS102", "subject_name": "Database Management", "mid_term_marks": 15, "cie_marks": 15, "total_internal": 30, "semester": 2},
        {"student_id": "2024001", "subject_code": "CS104", "subject_name": "Mathematics II", "mid_term_marks": 5, "cie_marks": 5, "total_internal": 10, "semester": 2},
        # Previous Semester (Sem 1) - Low grades to trigger Phase 3
        {"student_id": "2024001", "subject_code": "CS091", "subject_name": "C Programming", "mid_term_marks": 10, "cie_marks": 10, "total_internal": 20, "semester": 1},
        {"student_id": "2024001", "subject_code": "CS092", "subject_name": "Mathematics I", "mid_term_marks": 25, "cie_marks": 15, "total_internal": 40, "semester": 1}
    ]
    
    # Performance Records for Student 2 (Priya - WARNING)
    priya_perf = [
        {"student_id": "2024002", "subject_code": "CS101", "subject_name": "Data Structures", "mid_term_marks": 12, "cie_marks": 10, "total_internal": 22, "semester": 2},
        {"student_id": "2024002", "subject_code": "CS102", "subject_name": "Database Management", "mid_term_marks": 20, "cie_marks": 18, "total_internal": 38, "semester": 2},
        # Sem 1 Good grades (No Bridge Gap)
        {"student_id": "2024002", "subject_code": "CS091", "subject_name": "C Programming", "mid_term_marks": 25, "cie_marks": 20, "total_internal": 45, "semester": 1}
    ]

    # Performance Records for Student 3 (Amit - SAFE)
    amit_perf = [
        {"student_id": "2024003", "subject_code": "CS101", "subject_name": "Data Structures", "mid_term_marks": 28, "cie_marks": 20, "total_internal": 48, "semester": 2},
        {"student_id": "2024003", "subject_code": "CS102", "subject_name": "Database Management", "mid_term_marks": 25, "cie_marks": 20, "total_internal": 45, "semester": 2}
    ]

    await db.academic_performance.insert_many(rajesh_perf + priya_perf + amit_perf)

    # 5. Seed actual attendance logs for precision
    # CS101 for Rajesh (low attendance)
    logs = []
    for i in range(1, 21):
        status = "present" if i <= 8 else "absent"
        logs.append({"student_id": "2024001", "subject_code": "CS101", "status": status, "date": datetime.now()})
        # CS101 for Amit (high attendance)
        logs.append({"student_id": "2024003", "subject_code": "CS101", "status": "present", "date": datetime.now()})

    if logs:
        await db.attendance.insert_many(logs)

    print("✅ Presentation Data Ready!")
    print("👉 Use '2024001' to show a Critical Risk with a Prerequisite Bridge Gap.")
    print("👉 Use '2024003' to show a perfect Safe profile.")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_presentation_data())
