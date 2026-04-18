"""
Seed Script for Phase 2 & 3 - Academic Performance and Curriculum Mapping
This script populates MongoDB with:
1. academic_performance collection (student marks)
2. curriculum_map collection (prerequisite relationships)
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "edupath_db")

async def seed_database():
    """Seed Phase 2 and Phase 3 data"""
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("🌱 Seeding Phase 2 & 3 Data...\n")
    
    # ════════════════════════════════════════════════════════
    # STUDENTS COLLECTION (Required first)
    # ════════════════════════════════════════════════════════
    print("[Students] Seeding students collection...")
    
    students_data = [
        {
            "student_id": "2024001",
            "name": "Rajesh Kumar",
            "email": "rajesh.kumar@university.edu",
            "department": "CE",
            "semester": 2,
            "status": "active"
        },
        {
            "student_id": "2024002",
            "name": "Priya Singh",
            "email": "priya.singh@university.edu",
            "department": "IT",
            "semester": 2,
            "status": "active"
        },
        {
            "student_id": "2024003",
            "name": "Amit Patel",
            "email": "amit.patel@university.edu",
            "department": "EC",
            "semester": 2,
            "status": "active"
        }
    ]
    
    await db.students.delete_many({})
    result = await db.students.insert_many(students_data)
    print(f"✓ Inserted {len(result.inserted_ids)} student records")
    
    # ════════════════════════════════════════════════════════
    # PHASE 2: Academic Performance Collection
    # ════════════════════════════════════════════════════════
    print("\n[Phase 2] Seeding academic_performance collection...")
    
    academic_performance_data = [
        # Student 2024001 - Mixed performance (test case for diagnostic logic)
        {
            "student_id": "2024001",
            "subject_code": "CS101",
            "subject_name": "C Programming",
            "mid_term_marks": 18,  # Good
            "cie_marks": 15,  # Good
            "total_internal": 33,
            "semester": 1,
            "seeded_at": datetime.utcnow(),
        },
        {
            "student_id": "2024001",
            "subject_code": "MA101",
            "subject_name": "Mathematics",
            "mid_term_marks": 12,  # Low - Good for testing
            "cie_marks": 10,  # Low
            "total_internal": 22,
            "semester": 1,
            "seeded_at": datetime.utcnow(),
        },
        {
            "student_id": "2024001",
            "subject_code": "DS101",
            "subject_name": "Data Structures",
            "mid_term_marks": 20,  # Good
            "cie_marks": 18,  # Good
            "total_internal": 38,
            "semester": 2,
            "seeded_at": datetime.utcnow(),
        },
        {
            "student_id": "2024001",
            "subject_code": "ML101",
            "subject_name": "Machine Learning",
            "mid_term_marks": 8,  # CRITICAL - Links to weak Statistics
            "cie_marks": 7,  # CRITICAL
            "total_internal": 15,
            "semester": 2,
            "seeded_at": datetime.utcnow(),
        },
        {
            "student_id": "2024001",
            "subject_code": "STATS101",
            "subject_name": "Statistics",
            "mid_term_marks": 10,  # Low in prerequisite
            "cie_marks": 9,
            "total_internal": 19,
            "semester": 1,
            "seeded_at": datetime.utcnow(),
        },
        # Student 2024002 - Strong performer
        {
            "student_id": "2024002",
            "subject_code": "CS101",
            "subject_name": "C Programming",
            "mid_term_marks": 28,
            "cie_marks": 19,
            "total_internal": 47,
            "semester": 1,
            "seeded_at": datetime.utcnow(),
        },
        {
            "student_id": "2024002",
            "subject_code": "MA101",
            "subject_name": "Mathematics",
            "mid_term_marks": 25,
            "cie_marks": 18,
            "total_internal": 43,
            "semester": 1,
            "seeded_at": datetime.utcnow(),
        },
        {
            "student_id": "2024002",
            "subject_code": "DS101",
            "subject_name": "Data Structures",
            "mid_term_marks": 26,
            "cie_marks": 19,
            "total_internal": 45,
            "semester": 2,
            "seeded_at": datetime.utcnow(),
        },
        # Student 2024003 - Average performer with specific weak area
        {
            "student_id": "2024003",
            "subject_code": "ECE101",
            "subject_name": "Digital Electronics",
            "mid_term_marks": 14,
            "cie_marks": 11,
            "total_internal": 25,
            "semester": 1,
            "seeded_at": datetime.utcnow(),
        },
        {
            "student_id": "2024003",
            "subject_code": "MP101",
            "subject_name": "Microprocessors",
            "mid_term_marks": 16,
            "cie_marks": 13,
            "total_internal": 29,
            "semester": 2,
            "seeded_at": datetime.utcnow(),
        },
    ]
    
    # Clear existing data and insert
    await db.academic_performance.delete_many({})
    result = await db.academic_performance.insert_many(academic_performance_data)
    print(f"✓ Inserted {len(result.inserted_ids)} academic performance records")
    
    # Create index
    await db.academic_performance.create_index([("student_id", 1), ("subject_code", 1)])
    
    # ════════════════════════════════════════════════════════
    # PHASE 3: Curriculum Mapping Collection (Prerequisites)
    # ════════════════════════════════════════════════════════
    print("\n[Phase 3] Seeding curriculum_map collection...")
    
    curriculum_map_data = [
        # Core prerequisite chains
        {
            "prerequisite_subject": "C Programming",
            "prerequisite_code": "CS101",
            "current_subject": "Data Structures",
            "current_code": "DS101",
            "semester_gap": 1,
            "difficulty_multiplier": 1.2,
            "description": "Data Structures builds on C Programming fundamentals",
        },
        {
            "prerequisite_subject": "Statistics",
            "prerequisite_code": "STATS101",
            "current_subject": "Machine Learning",
            "current_code": "ML101",
            "semester_gap": 1,
            "difficulty_multiplier": 1.5,
            "description": "Machine Learning heavily relies on statistical foundations",
        },
        {
            "prerequisite_subject": "Digital Electronics",
            "prerequisite_code": "ECE101",
            "current_subject": "Microprocessors",
            "current_code": "MP101",
            "semester_gap": 1,
            "difficulty_multiplier": 1.3,
            "description": "Microprocessor design requires digital logic knowledge",
        },
        {
            "prerequisite_subject": "Mathematics",
            "prerequisite_code": "MA101",
            "current_subject": "Statistics",
            "current_code": "STATS101",
            "semester_gap": 1,
            "difficulty_multiplier": 1.1,
            "description": "Statistics is rooted in mathematical concepts",
        },
        {
            "prerequisite_subject": "Data Structures",
            "prerequisite_code": "DS101",
            "current_subject": "Database Systems",
            "current_code": "DB101",
            "semester_gap": 2,
            "difficulty_multiplier": 1.2,
            "description": "Database systems use advanced data structure concepts",
        },
        {
            "prerequisite_subject": "C Programming",
            "prerequisite_code": "CS101",
            "current_subject": "Operating Systems",
            "current_code": "OS101",
            "semester_gap": 2,
            "difficulty_multiplier": 1.3,
            "description": "OS implementation requires strong C programming skills",
        },
    ]
    
    # Clear existing data and insert
    await db.curriculum_map.delete_many({})
    result = await db.curriculum_map.insert_many(curriculum_map_data)
    print(f"✓ Inserted {len(result.inserted_ids)} curriculum mapping records")
    
    # Create index
    await db.curriculum_map.create_index([("prerequisite_code", 1), ("current_code", 1)])
    
    # ════════════════════════════════════════════════════════
    # Print Summary
    # ════════════════════════════════════════════════════════
    student_count = await db.students.count_documents({})
    perf_count = await db.academic_performance.count_documents({})
    map_count = await db.curriculum_map.count_documents({})
    
    print(f"\n{'='*60}")
    print(f"✓ Seed Complete!")
    print(f"  • Student Records: {student_count}")
    print(f"  • Academic Performance Records: {perf_count}")
    print(f"  • Curriculum Mappings: {map_count}")
    print(f"{'='*60}")
    print(f"\nTest Data Prepared:")
    print(f"  → Student 2024001: Mixed performance (CRITICAL in ML, GOOD in CS)")
    print(f"  → Student 2024002: Strong performer across all subjects")
    print(f"  → Student 2024003: Weak in Digital Electronics (testing prerequisite chain)")
    print(f"\nPrerequisite Chains:")
    for mapping in curriculum_map_data:
        print(f"  → {mapping['prerequisite_subject']} → {mapping['current_subject']}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
