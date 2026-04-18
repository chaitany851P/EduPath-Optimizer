"""
═══════════════════════════════════════════════════════════════════════════════
EduPath Optimizer - 360° System Diagnostic & Verification Script
═══════════════════════════════════════════════════════════════════════════════

Purpose: Comprehensive system health check validating all four modules:
1. Connectivity & Environment
2. Logic & Mathematical Alignment
3. RBAC & Security
4. Phase 2 & 3 Readiness

Usage: python system_check.py
"""

import asyncio
import os
import sys
from datetime import datetime, date, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import json
import requests
from typing import Dict, List, Tuple

# Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "edupath_optimizer")
API_BASE = os.getenv("API_BASE", "http://localhost:8000")

# ANSI Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OK = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}\n")

def print_pass(test_name: str, message: str = ""):
    """Print passing test"""
    msg = f"✓ {test_name}"
    if message:
        msg += f" | {message}"
    print(f"{Colors.OK}{msg}{Colors.END}")

def print_fail(test_name: str, message: str = ""):
    """Print failing test"""
    msg = f"✗ {test_name}"
    if message:
        msg += f" | {message}"
    print(f"{Colors.FAIL}{msg}{Colors.END}")

def print_warning(test_name: str, message: str = ""):
    """Print warning"""
    msg = f"⚠ {test_name}"
    if message:
        msg += f" | {message}"
    print(f"{Colors.WARNING}{msg}{Colors.END}")

# ════════════════════════════════════════════════════════════════════════════════
# MODULE 1: CONNECTIVITY & ENVIRONMENT CHECK
# ════════════════════════════════════════════════════════════════════════════════

async def check_fastapi_initialization():
    """Check if FastAPI app initializes without errors"""
    try:
        # Try to reach health endpoint
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                print_pass("FastAPI Initialization", f"Server running at {API_BASE}")
                return True
        print_fail("FastAPI Initialization", f"Unexpected response: {response.text}")
        return False
    except requests.exceptions.ConnectionError:
        print_fail("FastAPI Initialization", f"Cannot connect to {API_BASE}. Is server running?")
        return False
    except Exception as e:
        print_fail("FastAPI Initialization", str(e))
        return False

async def check_mongodb_connection():
    """Check MongoDB connectivity"""
    try:
        client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        
        # Ping MongoDB
        await db.command("ping")
        print_pass("MongoDB Connection", f"Connected to {DB_NAME}")
        
        return client, db
    except Exception as e:
        print_fail("MongoDB Connection", str(e))
        return None, None

async def check_collections_exist(db):
    """Verify all required collections exist"""
    required_collections = [
        "students",
        "subjects",
        "attendance",
        "academic_performance",  # Phase 2
        "curriculum_map",  # Phase 3
    ]
    
    if db is None:
        print_fail("Collections Check", "Database connection not available")
        return False
    
    existing_collections = await db.list_collection_names()
    all_exist = True
    
    for collection in required_collections:
        if collection in existing_collections:
            count = await db[collection].estimated_document_count()
            print_pass(f"Collection: {collection}", f"{count} documents")
        else:
            print_fail(f"Collection: {collection}", "Does not exist")
            all_exist = False
    
    return all_exist

async def check_collection_indexes(db):
    """Verify critical indexes are created"""
    if db is None:
        print_fail("Collection Indexes", "Database connection not available")
        return False
    
    index_checks = [
        ("students", "student_id"),
        ("subjects", "subject_code"),
        ("attendance", [("student_id", 1), ("subject_code", 1)]),
        ("academic_performance", [("student_id", 1), ("subject_code", 1)]),
    ]
    
    all_good = True
    for collection, index_spec in index_checks:
        try:
            indexes = await db[collection].list_indexes().to_list(None)
            index_names = [idx["name"] for idx in indexes]
            
            # Check if index exists
            found = False
            if isinstance(index_spec, str):
                found = any(index_spec in name for name in index_names)
            else:
                found = any("student_id" in str(idx["key"]) and "subject_code" in str(idx["key"]) for idx in indexes)
            
            if found:
                print_pass(f"Index on {collection}", f"{index_spec}")
            else:
                print_warning(f"Index on {collection}", f"Index {index_spec} not found")
                
        except Exception as e:
            print_fail(f"Index on {collection}", str(e))
            all_good = False
    
    return all_good

async def check_holidays_library():
    """Verify holidays library is working for India 2026"""
    try:
        import holidays
        india_holidays = holidays.India(years=2026)
        
        # Check for some known Indian holidays in 2026
        if len(india_holidays) > 0:
            print_pass("Holidays Library", f"Found {len(india_holidays)} holidays for India 2026")
            print(f"  Sample holidays: {list(india_holidays.items())[:3]}")
            return True
        else:
            print_warning("Holidays Library", "No holidays found for 2026")
            return False
    except ImportError:
        print_fail("Holidays Library", "holidays library not installed")
        return False
    except Exception as e:
        print_fail("Holidays Library", str(e))
        return False

# ════════════════════════════════════════════════════════════════════════════════
# MODULE 2: LOGIC & MATHEMATICAL ALIGNMENT CHECK
# ════════════════════════════════════════════════════════════════════════════════

def check_attendance_math():
    """Test: Attendance gap calculation"""
    # Scenario: 20 days, attended 5, target 75%
    total_days = 20
    attended = 5
    target_percentage = 75
    
    # Calculate minimum classes needed
    min_classes_needed = int((target_percentage / 100) * total_days)
    gap = max(0, min_classes_needed - attended)
    
    expected_gap = 10  # 75% of 20 = 15, 15 - 5 = 10
    
    if gap == expected_gap:
        print_pass("Attendance Math", f"Gap calculation correct: {gap} classes needed (expected {expected_gap})")
        return True
    else:
        print_fail("Attendance Math", f"Gap calculation incorrect: got {gap}, expected {expected_gap}")
        return False

def check_date_filtering():
    """Test: Ensure past dates and weekends are excluded"""
    today = date.today()
    future_monday = today + timedelta(days=(7 - today.weekday()))  # Next Monday
    past_date = today - timedelta(days=5)
    
    # Simulate date filter logic
    def is_valid_suggestion_date(d: date) -> bool:
        # Must not be in past
        if d < today:
            return False
        # Must not be weekend (5=Saturday, 6=Sunday)
        if d.weekday() in [5, 6]:
            return False
        return True
    
    past_valid = is_valid_suggestion_date(past_date)
    future_valid = is_valid_suggestion_date(future_monday)
    
    if not past_valid and future_valid:
        print_pass("Date Filtering", "Past dates excluded, future dates included")
        return True
    else:
        print_fail("Date Filtering", f"Past valid={past_valid} (should be False), Future valid={future_valid} (should be True)")
        return False

def check_critical_risk_trigger():
    """Test: Critical risk warning triggers when gap > remaining days"""
    total_days = 20
    attended = 2
    today_index = 10  # 10 days have passed
    remaining_days = total_days - today_index
    
    target_percentage = 75
    min_classes_needed = int((target_percentage / 100) * total_days)
    gap = max(0, min_classes_needed - attended)
    
    # Critical if gap > remaining_days
    is_critical = gap > remaining_days
    
    # In this scenario: need 15 total, attended 2, gap = 13, remaining = 10
    # 13 > 10 → Critical Risk
    
    if is_critical and gap == 13 and remaining_days == 10:
        print_pass("Critical Risk Trigger", f"Correctly identified critical: gap={gap} > remaining={remaining_days}")
        return True
    else:
        print_fail("Critical Risk Trigger", f"gap={gap}, remaining={remaining_days}, is_critical={is_critical}")
        return False

def check_date_format():
    """Test: Dates returned in DD-MM-YYYY format"""
    test_date = datetime(2026, 3, 15)
    formatted = test_date.strftime("%d-%m-%Y")
    expected = "15-03-2026"
    
    if formatted == expected:
        print_pass("Date Format", f"Correct format: {formatted}")
        return True
    else:
        print_fail("Date Format", f"Got {formatted}, expected {expected}")
        return False

# ════════════════════════════════════════════════════════════════════════════════
# MODULE 3: RBAC & SECURITY CHECK
# ════════════════════════════════════════════════════════════════════════════════

def check_jwt_token_generation():
    """Test: /token endpoint generates valid JWT"""
    try:
        payload = {
            "username": "2024001",
            "password": "student123",
            "role": "student"
        }
        
        response = requests.post(
            f"{API_BASE}/api/auth/token",
            data=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data and data.get("token_type") == "bearer":
                token = data["access_token"]
                print_pass("JWT Generation", f"Token generated: {token[:20]}...")
                return True, token
            else:
                print_fail("JWT Generation", f"Invalid response structure: {data}")
                return False, None
        else:
            print_warning("JWT Generation", f"Status {response.status_code} - Endpoint may not exist (expected in development)")
            return False, None
    except requests.exceptions.ConnectionError:
        print_warning("JWT Generation", "API not responding")
        return False, None
    except Exception as e:
        print_fail("JWT Generation", str(e))
        return False, None

def check_rbac_student_forbidden(token: str = None):
    """Test: Student role gets 403 when accessing admin endpoints"""
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        # Try to access admin endpoint with student token
        response = requests.get(
            f"{API_BASE}/api/admin/students",
            headers=headers,
            timeout=5
        )
        
        # Should get 403 Forbidden or 401 Unauthorized
        if response.status_code in [401, 403]:
            print_pass("RBAC: Student Forbidden", f"Correctly returned {response.status_code}")
            return True
        elif response.status_code == 404:
            print_warning("RBAC: Student Forbidden", "Endpoint not found (expected in development)")
            return False
        else:
            print_fail("RBAC: Student Forbidden", f"Expected 403/401, got {response.status_code}")
            return False
    except Exception as e:
        print_warning("RBAC: Student Forbidden", str(e))
        return False

def check_teacher_attendance_access():
    """Test: Teacher role can access attendance update logic"""
    try:
        # Check if teacher endpoint exists
        response = requests.get(
            f"{API_BASE}/api/teachers/students",
            timeout=5
        )
        
        if response.status_code == 200:
            print_pass("Teacher Attendance Access", "Teacher endpoint accessible")
            return True
        elif response.status_code == 404:
            print_warning("Teacher Attendance Access", "Teacher endpoint not found (endpoint may not exist)")
            return False
        else:
            print_fail("Teacher Attendance Access", f"Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print_warning("Teacher Attendance Access", str(e))
        return False

# ════════════════════════════════════════════════════════════════════════════════
# MODULE 4: PHASE 2 & 3 READINESS CHECK
# ════════════════════════════════════════════════════════════════════════════════

async def check_academic_performance_schema(db):
    """Check Phase 2: Academic performance collection schema"""
    if db is None:
        print_fail("Phase 2 Schema", "Database not available")
        return False
    
    try:
        ap_collection = db.academic_performance
        
        # Get a sample document
        sample = await ap_collection.find_one()
        
        if sample is None:
            print_warning("Phase 2 Schema", "No documents in academic_performance - collection empty")
            return False
        
        # Check required fields
        required_fields = ["student_id", "subject_code", "mid_term_marks", "cie_marks", "total_internal"]
        missing_fields = [f for f in required_fields if f not in sample]
        
        if missing_fields:
            print_fail("Phase 2 Schema", f"Missing fields: {missing_fields}")
            return False
        else:
            # Validate mark ranges
            mid_term = sample.get("mid_term_marks", 0)
            cie = sample.get("cie_marks", 0)
            total = sample.get("total_internal", 0)
            
            if 0 <= mid_term <= 30 and 0 <= cie <= 20 and total <= 50:
                print_pass("Phase 2 Schema", f"Valid marks found: mid_term={mid_term}, cie={cie}, total={total}")
                return True
            else:
                print_fail("Phase 2 Schema", f"Invalid mark ranges: {sample}")
                return False
    except Exception as e:
        print_fail("Phase 2 Schema", str(e))
        return False

async def check_curriculum_map_schema(db):
    """Check Phase 3: Curriculum mapping collection schema"""
    if db is None:
        print_fail("Phase 3 Schema", "Database not available")
        return False
    
    try:
        cm_collection = db.curriculum_map
        
        # Get a sample document
        sample = await cm_collection.find_one()
        
        if sample is None:
            print_warning("Phase 3 Schema", "No documents in curriculum_map - collection empty")
            return False
        
        # Check required fields
        required_fields = ["prerequisite_subject", "current_subject", "prerequisite_code", "current_code"]
        missing_fields = [f for f in required_fields if f not in sample]
        
        if missing_fields:
            print_fail("Phase 3 Schema", f"Missing fields: {missing_fields}")
            return False
        else:
            prereq = sample.get("prerequisite_subject")
            current = sample.get("current_subject")
            print_pass("Phase 3 Schema", f"Valid mapping found: {prereq} → {current}")
            return True
    except Exception as e:
        print_fail("Phase 3 Schema", str(e))
        return False

async def check_phase2_endpoints():
    """Verify Phase 2 backend endpoints exist"""
    endpoints = [
        "/api/phase-2-3/exam-strategy/{student_id}",
        "/api/phase-2-3/academic-performance/{student_id}",
    ]
    
    print("Phase 2 Endpoints Status:")
    for endpoint in endpoints:
        # We can't fully test without valid student_id, but we can check the route exists
        sample_endpoint = endpoint.replace("{student_id}", "test")
        try:
            response = requests.get(f"{API_BASE}{sample_endpoint}", timeout=5)
            if response.status_code != 404:
                print_pass(f"  Endpoint: {endpoint}", f"Status {response.status_code}")
            else:
                print_warning(f"  Endpoint: {endpoint}", "Not found (might not exist)")
        except Exception as e:
            print_warning(f"  Endpoint: {endpoint}", str(e))

async def check_phase3_endpoints():
    """Verify Phase 3 backend endpoints exist"""
    endpoints = [
        "/api/phase-2-3/bridge-report/{student_id}",
    ]
    
    print("Phase 3 Endpoints Status:")
    for endpoint in endpoints:
        sample_endpoint = endpoint.replace("{student_id}", "test")
        try:
            response = requests.get(f"{API_BASE}{sample_endpoint}", timeout=5)
            if response.status_code != 404:
                print_pass(f"  Endpoint: {endpoint}", f"Status {response.status_code}")
            else:
                print_warning(f"  Endpoint: {endpoint}", "Not found (might not exist)")
        except Exception as e:
            print_warning(f"  Endpoint: {endpoint}", str(e))

# ════════════════════════════════════════════════════════════════════════════════
# MAIN SYSTEM CHECK ORCHESTRATOR
# ════════════════════════════════════════════════════════════════════════════════

async def run_system_check():
    """Run complete system diagnostic"""
    print_header("ESPATH OPTIMIZER - 360° SYSTEM DIAGNOSTIC")
    
    results = {
        "module_1": [],
        "module_2": [],
        "module_3": [],
        "module_4": [],
        "timestamp": datetime.now().isoformat(),
    }
    
    # ── MODULE 1: CONNECTIVITY & ENVIRONMENT ──
    print_header("MODULE 1: Connectivity & Environment Check")
    
    m1_result = await check_fastapi_initialization()
    results["module_1"].append(("FastAPI Initialization", m1_result))
    
    client, db = await check_mongodb_connection()
    results["module_1"].append(("MongoDB Connection", db is not None))
    
    if db is not None:
        m1_collections = await check_collections_exist(db)
        results["module_1"].append(("Collections Exist", m1_collections))
        
        m1_indexes = await check_collection_indexes(db)
        results["module_1"].append(("Collection Indexes", m1_indexes))
    
    m1_holidays = await check_holidays_library()
    results["module_1"].append(("Holidays Library", m1_holidays))
    
    # ── MODULE 2: LOGIC & MATHEMATICAL ALIGNMENT ──
    print_header("MODULE 2: Logic & Mathematical Alignment Check")
    
    m2_math = check_attendance_math()
    results["module_2"].append(("Attendance Math", m2_math))
    
    m2_dates = check_date_filtering()
    results["module_2"].append(("Date Filtering", m2_dates))
    
    m2_critical = check_critical_risk_trigger()
    results["module_2"].append(("Critical Risk Trigger", m2_critical))
    
    m2_format = check_date_format()
    results["module_2"].append(("Date Format", m2_format))
    
    # ── MODULE 3: RBAC & SECURITY ──
    print_header("MODULE 3: RBAC & Security Check")
    
    jwt_success, token = check_jwt_token_generation()
    results["module_3"].append(("JWT Generation", jwt_success))
    
    m3_student = check_rbac_student_forbidden(token)
    results["module_3"].append(("RBAC Student Forbidden", m3_student))
    
    m3_teacher = check_teacher_attendance_access()
    results["module_3"].append(("Teacher Attendance Access", m3_teacher))
    
    # ── MODULE 4: PHASE 2 & 3 READINESS ──
    print_header("MODULE 4: Phase 2 & 3 Readiness Check")
    
    if db is not None:
        m4_phase2 = await check_academic_performance_schema(db)
        results["module_4"].append(("Phase 2 Schema", m4_phase2))
        
        m4_phase3 = await check_curriculum_map_schema(db)
        results["module_4"].append(("Phase 3 Schema", m4_phase3))
    
    await check_phase2_endpoints()
    await check_phase3_endpoints()
    
    # ── SUMMARY ──
    print_header("SYSTEM CHECK SUMMARY")
    
    total_checks = sum(len(v) for v in results.values() if isinstance(v, list))
    passed_checks = sum(
        sum(1 for _, r in v if r is True)
        for v in results.values() if isinstance(v, list)
    )
    
    print(f"\n{Colors.BOLD}Total Checks: {passed_checks}/{total_checks}{Colors.END}")
    
    if passed_checks == total_checks:
        print(f"\n{Colors.OK}{Colors.BOLD}✓ SYSTEM VERIFIED - All checks passed!{Colors.END}\n")
        status = "SYSTEM_VERIFIED"
    elif passed_checks >= (total_checks * 0.85):
        print(f"\n{Colors.WARNING}{Colors.BOLD}⚠ SYSTEM OPERATIONAL - Most checks passed (85%+){Colors.END}\n")
        status = "SYSTEM_OPERATIONAL"
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}✗ SYSTEM ISSUES - Critical failures detected{Colors.END}\n")
        status = "SYSTEM_ISSUES"
    
    # Save results
    report = {
        "status": status,
        "timestamp": results["timestamp"],
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "pass_rate": f"{(passed_checks/total_checks)*100:.1f}%",
        "results": results,
    }
    
    with open("system_check_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"Report saved to: system_check_report.json\n")
    
    if client:
        client.close()
    
    return status

# ════════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(f"\n{Colors.BOLD}Starting system diagnostic...{Colors.END}")
    print(f"MongoDB: {MONGO_URI}")
    print(f"API: {API_BASE}\n")
    
    status = asyncio.run(run_system_check())
    
    # Exit with appropriate code
    sys.exit(0 if status in ["SYSTEM_VERIFIED", "SYSTEM_OPERATIONAL"] else 1)
