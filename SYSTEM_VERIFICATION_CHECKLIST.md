# EduPath Optimizer - System Verification Checklist & Troubleshooting

## 📋 Manual Verification Checklist

Use this checklist to manually verify system components that may not be covered by the automated script.

### MODULE 1: Connectivity & Environment

#### 1.1 FastAPI Server Status
- [ ] Server starts without errors: `python backend/main.py`
- [ ] Health endpoint responds: `curl http://localhost:8000/health`
- [ ] Response shows: `{"status": "healthy"}`
- [ ] Server version is 2.0.0 or higher

#### 1.2 MongoDB Connection
- [ ] MongoDB running (Atlas or local)
- [ ] Can connect with MongoDB Compass
- [ ] Database name: `edupath_optimizer`
- [ ] Collections load without lag

#### 1.3 Required Collections Verification
- [ ] ✓ `students` - Contains student records
- [ ] ✓ `subjects` - Contains subject codes and names
- [ ] ✓ `attendance` - Contains attendance records
- [ ] ✓ `academic_performance` - Contains marks (NEW - Phase 2)
- [ ] ✓ `curriculum_map` - Contains prerequisites (NEW - Phase 3)
- [ ] Check: `db.getCollectionNames()` returns all 5+

#### 1.4 Indexes Created
- [ ] `students`: unique index on `student_id`
- [ ] `subjects`: unique index on `subject_code`
- [ ] `attendance`: compound index on `(student_id, subject_code, date)`
- [ ] `academic_performance`: compound index on `(student_id, subject_code)`
- [ ] `curriculum_map`: compound index on `(prerequisite_code, current_code)`

#### 1.5 Environment Variables
- [ ] `MONGO_URI` set (or using default)
- [ ] `DB_NAME` set to `edupath_optimizer`
- [ ] API running on port 8000 (or configured port)
- [ ] Check: `.env` file contains all required vars

#### 1.6 Dependencies Installed
```bash
pip list | grep -E "fastapi|motor|pydantic|pymongo|holidays"
```
- [ ] fastapi (2.0+)
- [ ] motor (async MongoDB)
- [ ] pydantic (validation)
- [ ] pymongo (MongoDB driver)
- [ ] holidays (2026 India holidays)

---

### MODULE 2: Logic & Mathematical Alignment

#### 2.1 Attendance Calculation Test

**Scenario:** 
- Total classes: 100
- Classes attended: 50
- Target: 75%

**Expected Result:**
- Minimum classes needed: 75
- Gap to fill: 25

**How to Test:**
```bash
curl -X POST http://localhost:8000/api/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "2024001",
    "semester_end_date": "2026-05-31",
    "upcoming_leave_dates": []
  }'
```

- [ ] Gap calculation matches expectation
- [ ] Feasibility status correct
- [ ] Buffer classes calculated

#### 2.2 Date Validation Test

**Rules to Verify:**
1. Past dates never suggested
2. Weekends (Saturday/Sunday) excluded
3. Indian holidays excluded
4. Dates in DD-MM-YYYY format

**How to Test:**
- Request strategy for today
- Check no dates are before today
- Check no dates are weekends
- Verify format is DD-MM-YYYY

- [ ] All dates are in future
- [ ] No weekends included
- [ ] No holidays included
- [ ] Format is DD-MM-YYYY

#### 2.3 Critical Risk Trigger Test

**Scenario:**
- Days remaining: 10
- Classes needed to reach 75%: 15
- Gap (15 - 15) = 0

**Expected:** No critical warning

**Test Another Scenario:**
- Days remaining: 5
- Classes needed: 20
- Gap = 15

**Expected:** CRITICAL (gap 15 > remaining 5)

- [ ] Critical risk triggers when appropriate
- [ ] Warning triggers for partial risk
- [ ] Safe status for meeting targets

#### 2.4 Date Range Handling

- [ ] Can handle requests spanning multiple months
- [ ] Can handle requests within 1 week
- [ ] Can handle requests spanning full semester
- [ ] No date overflow errors

---

### MODULE 3: RBAC & Security Check

#### 3.1 JWT Token Generation

```bash
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/json" \
  -d '{"username": "student_001", "password": "pass", "role": "student"}'
```

- [ ] Returns 200 status
- [ ] Response contains `access_token`
- [ ] Response contains `token_type: "bearer"`
- [ ] Token is not empty

#### 3.2 Student Role Access Control

**Test:** Try to access admin endpoint WITHOUT token
```bash
curl http://localhost:8000/api/admin/students
```
- [ ] Returns 401 Unauthorized or 403 Forbidden
- [ ] Does not return 200 (not granted access)

**Test:** Try to access student endpoint WITH student token
```bash
curl -H "Authorization: Bearer {token}" \
  http://localhost:8000/api/students/{student_id}
```
- [ ] Returns 200 or 404 (not denied)
- [ ] Returns student data

#### 3.3 Teacher Role Access

**Test:** Teacher can access attendance endpoints
```bash
curl -H "Authorization: Bearer {teacher_token}" \
  http://localhost:8000/api/teachers/subjects
```
- [ ] Returns 200
- [ ] Shows teacher's subjects

**Test:** Teacher cannot access admin endpoints
```bash
curl -H "Authorization: Bearer {teacher_token}" \
  http://localhost:8000/api/admin/add-fest
```
- [ ] Returns 403 Forbidden (not 200)

#### 3.4 Admin Role Access

- [ ] Admin can access all endpoints
- [ ] Admin can view all students
- [ ] Admin can manage all subjects
- [ ] Admin can execute admin commands

#### 3.5 Token Expiration (if implemented)

- [ ] Tokens expire after configured time
- [ ] Expired tokens return 401
- [ ] Refresh token works if implemented

---

### MODULE 4: Phase 2 & 3 Readiness Check

#### 4.1 Phase 2: Academic Performance Collection

**Check Schema:**
```javascript
db.academic_performance.findOne()
```

Required fields present:
- [ ] `student_id`: String
- [ ] `subject_code`: String
- [ ] `subject_name`: String
- [ ] `mid_term_marks`: Number (0-30)
- [ ] `cie_marks`: Number (0-20)
- [ ] `total_internal`: Number (0-50)
- [ ] `semester`: Number
- [ ] `upload_date`: Date

**Validation Rules:**
- [ ] mid_term_marks between 0-30
- [ ] cie_marks between 0-20
- [ ] total_internal = mid_term + cie
- [ ] student_id matches existing student
- [ ] subject_code matches existing subject

**Test Phase 2 Endpoint:**
```bash
curl http://localhost:8000/api/phase-2-3/exam-strategy/2024001
```
- [ ] Returns 200 status
- [ ] Response contains risk levels (CRITICAL_RISK/WARNING/SAFE)
- [ ] Priority scores calculated
- [ ] Study list ordered by priority
- [ ] Messages include revision focus

#### 4.2 Phase 3: Curriculum Mapping Collection

**Check Schema:**
```javascript
db.curriculum_map.findOne()
```

Required fields present:
- [ ] `prerequisite_subject`: String (e.g., "C Programming")
- [ ] `prerequisite_code`: String (e.g., "CS101")
- [ ] `current_subject`: String (e.g., "Data Structures")
- [ ] `current_code`: String (e.g., "DS101")
- [ ] `semester_gap`: Number
- [ ] `difficulty_multiplier`: Number

**Mappings Should Include:**
- [ ] C Programming → Data Structures
- [ ] Statistics → Machine Learning
- [ ] Digital Electronics → Microprocessors
- [ ] Mathematics → Statistics
- [ ] Data Structures → Database Systems
- [ ] C Programming → Operating Systems

**Test Phase 3 Endpoint:**
```bash
curl http://localhost:8000/api/phase-2-3/bridge-report/2024001
```
- [ ] Returns 200 status
- [ ] Detects prerequisite gaps
- [ ] Includes gap severity (CRITICAL/HIGH/MEDIUM/LOW)
- [ ] Provides 5-day refresher plans
- [ ] Lists recommendations

#### 4.3 Teacher Marks Upload

**Test CSV Upload:**
```bash
curl -X POST "http://localhost:8000/api/teachers/upload-marks/csv?subject_code=CS101" \
  -F "file=@marks.csv"
```
- [ ] Accepts CSV file
- [ ] Returns 200 status
- [ ] Validates marks ranges
- [ ] Reports errors in response
- [ ] Updates academic_performance collection

**CSV Format Validation:**
- [ ] Header: student_id, subject_code, subject_name, mid_term_marks, cie_marks
- [ ] mid_term_marks: 0-30 range enforced
- [ ] cie_marks: 0-20 range enforced
- [ ] Student IDs validated
- [ ] Subject codes validated

**Test JSON Upload:**
```bash
curl -X POST "http://localhost:8000/api/teachers/upload-marks/bulk" \
  -H "Content-Type: application/json" \
  -d '[{"student_id":"2024001",...}]'
```
- [ ] Accepts JSON array
- [ ] Validates each entry
- [ ] Returns success/failure count
- [ ] Updates database

#### 4.4 Student Dashboard Update

**Phase 2 Tab:**
- [ ] Navigable via sidebar icon (📚)
- [ ] Displays exam readiness analysis
- [ ] Shows risk levels (red/yellow/green)
- [ ] Lists subjects with priority scores
- [ ] Includes revision strategies
- [ ] Color-coded study table

**Phase 3 Tab:**
- [ ] Navigable via sidebar icon (🌉)
- [ ] Shows foundation gap alerts
- [ ] Lists prerequisites with gaps
- [ ] Provides 5-day plans
- [ ] Includes recommendations
- [ ] Gap severity badges displayed

#### 4.5 Data Seeding

**Run seed script:**
```bash
python seed_phase2_3.py
```
- [ ] Script runs without errors
- [ ] Creates academic_performance documents
- [ ] Creates curriculum_map documents
- [ ] Test data includes:
  - [ ] Student 2024001 (mixed performance)
  - [ ] Student 2024002 (strong)
  - [ ] Student 2024003 (weak in Digital Electronics)
- [ ] Documents contain valid data

---

## 🔧 Troubleshooting Table

### Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| **500 Internal Server Error** | Unhandled exception in backend | Check `main.py` logs; ensure all imports work; verify DB connection |
| **KeyError: 'student_id'** | Missing field in document | Run seed script; verify documents have all required fields |
| **MongoServerError: cannot create index** | Index creation failed | Delete collection and reseed; check for duplicate index definitions |
| **Connection refused (localhost:8000)** | FastAPI not running | Start backend: `python backend/main.py` |
| **Connection refused (MongoDB)** | MongoDB not running | Start MongoDB; check URI in `.env` |
| **Empty study list in Phase 2** | No academic performance data | Run seed script or upload marks via CSV |
| **No gaps found in Phase 3** | Missing curriculum mappings | Run seed script; verify prerequisite mappings exist |
| **CSV upload: student not found** | Student ID doesn't exist in system | Create student first or use correct ID |
| **CSV upload: mid_term > 30** | Invalid mark value | Ensure mid_term_marks ≤ 30 |
| **CSV upload: cie > 20** | Invalid mark value | Ensure cie_marks ≤ 20 |
| **404 Not Found on Phase 2 endpoint** | Route not registered | Verify phase_2_3 router imported in main.py |
| **403 Forbidden (student accessing admin)** | RBAC working correctly | Expected behavior; student shouldn't access admin |
| **Token expired** | JWT not valid | Generate new token; check expiration settings |
| **Dates include weekends** | Weekend filter not applied | Check `date.weekday()` filter in code |
| **Dates include past dates** | Past date filter not applied | Verify comparison with `today` date |
| **Dates not in DD-MM-YYYY** | Format not applied | Check `strftime("%d-%m-%Y")` formatting |
| **Gap calculation wrong** | Math error in formula | Verify: `(target% / 100) * total_days` formula |
| **Critical risk not triggered** | Logic error | Check: `gap > remaining_days` comparison |
| **No holidays loaded** | holidays library issue | Install: `pip install holidays`; verify India timezone |

### Error Recovery Steps

#### For 500 Errors
1. Check backend console for stack trace
2. Verify all environment variables set
3. Test MongoDB connection: `mongo --eval "db.adminCommand('ping')"`
4. Restart Flask app: `python backend/main.py`
5. Check logs for specific error

#### For Database Errors
1. Connect with MongoDB Compass
2. Verify collections exist: `db.getCollectionNames()`
3. Check document count: `db.collection_name.count()`
4. View sample document: `db.collection_name.findOne()`
5. Reseed if corrupted: `python seed_phase2_3.py`

#### For API Route Errors
1. Verify route is registered in `main.py`
2. Check router file exists and has correct imports
3. Test endpoint with curl: `curl http://localhost:8000/api/path`
4. Check request method: GET vs POST vs PUT
5. Validate JSON request body

#### For Frontend Issues
1. Open browser console (F12)
2. Check Network tab for API requests
3. Verify `sessionStorage` has token
4. Check `student_id` stored correctly
5. Inspect element styling if CSS issues

---

## 📊 System Health Status

### Green (✓ All Good)
- All 4 modules passing all tests
- Pass rate: 100%
- Status: **SYSTEM_VERIFIED**
- Action: Safe to deploy

### Yellow (⚠ Operational)
- 3 modules passing, 1 module with issues
- OR all modules passing but with warnings
- Pass rate: 85-99%
- Status: **SYSTEM_OPERATIONAL**
- Action: Review warnings before deployment

### Red (✗ Issues)
- Multiple failures across modules
- Pass rate: < 85%
- Status: **SYSTEM_ISSUES**
- Action: Fix failures before deployment

---

## 🎯 Running the Full Diagnostic

### Step 1: Prepare Environment
```bash
cd e:\SGP\EduPath_Optimizer

# Ensure MongoDB is running
# Ensure FastAPI backend is running: python backend/main.py

# Install any missing dependencies
pip install -r backend/requirements.txt
```

### Step 2: Run Automated Script
```bash
python system_check.py
```

### Step 3: Review Report
```bash
# Check generated report
cat system_check_report.json
```

### Step 4: Manual Verification
Use the checklist above to verify:
- Critical features
- Edge cases
- UI interactions
- Data accuracy

### Step 5: Document Results
Create a report containing:
- System status (VERIFIED/OPERATIONAL/ISSUES)
- Pass rate percentage
- Any failures found
- Recommended actions

---

## 📝 Pre-Deployment Checklist

Before deploying to production:

- [ ] All Module 1 tests passing (100%)
- [ ] All Module 2 tests passing (100%)
- [ ] All Module 3 tests passing (100%)
- [ ] All Module 4 tests passing (100%)
- [ ] Manual checklist items verified
- [ ] PDF report generated with results
- [ ] Staging test completed
- [ ] Team review completed
- [ ] Rollback plan documented
- [ ] Monitoring alerts configured

---

## 📈 Performance Benchmarks

Use these benchmarks to validate system performance:

| Operation | Target Time | Acceptable Range |
|-----------|-------------|------------------|
| Get exam strategy | 45ms | 30-100ms |
| Get bridge report | 50ms | 30-100ms |
| Upload 60-row CSV | 800ms | 500-1500ms |
| Prerequisite query | 30ms | 15-75ms |
| Mark retrieval | 15ms | 10-50ms |
| Token generation | 100ms | 50-200ms |
| Dashboard load | 500ms | 300-1000ms |

If exceeding target times, consider:
- Adding database indexes
- Optimizing queries
- Caching results
- Scaling infrastructure

---

## 🎓 Conclusion

This comprehensive diagnostic validates:
✅ System connectivity and stability
✅ Mathematical logic correctness  
✅ Security and RBAC implementation
✅ Phase 2 & 3 feature readiness

**When all tests pass → You're ready for production deployment!**

---

**Generated:** April 2026  
**Version:** 2.0.0  
**Status:** Ready for System Verification
