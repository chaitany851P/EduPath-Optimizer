# System Check - Quick Start Guide

## 🚀 Run System Diagnostic in 5 Minutes

### Prerequisites
- ✅ FastAPI backend running: `python backend/main.py`
- ✅ MongoDB running (local or Atlas)
- ✅ Python 3.8+ installed
- ✅ All requirements installed: `pip install -r backend/requirements.txt`

---

## Step 1: Navigate to Project Directory
```bash
cd e:\SGP\EduPath_Optimizer
```

---

## Step 2: Run the System Check Script
```bash
python system_check.py
```

**Expected output:**
```
═══════════════════════════════════════════════════════════════════════════════
ESPATH OPTIMIZER - 360° SYSTEM DIAGNOSTIC
═══════════════════════════════════════════════════════════════════════════════

[MODULE 1 CHECKS RUNNING...]
✓ FastAPI Initialization | Server running at http://localhost:8000
✓ MongoDB Connection | Connected to edupath_optimizer
✓ Collection: students | 50 documents
✓ Collection: subjects | 25 documents
✓ Collection: attendance | 1000+ documents
✓ Collection: academic_performance | 10 documents
✓ Collection: curriculum_map | 6 documents
✓ Holidays Library | Found 16 holidays for India 2026

[MODULE 2 CHECKS RUNNING...]
✓ Attendance Math | Gap calculation correct: 10 classes needed (expected 10)
✓ Date Filtering | Past dates excluded, future dates included
✓ Critical Risk Trigger | Correctly identified critical: gap=13 > remaining=10
✓ Date Format | Correct format: 15-03-2026

[MODULE 3 CHECKS RUNNING...]
✓ JWT Generation | Token generated: eyJhbGciOiJIUzI1NiIs...
✓ RBAC: Student Forbidden | Correctly returned 403
✓ Teacher Attendance Access | Teacher endpoint accessible

[MODULE 4 CHECKS RUNNING...]
✓ Phase 2 Schema | Valid marks found: mid_term=18, cie=15, total=33
✓ Phase 3 Schema | Valid mapping found: C Programming → Data Structures
✓ Phase 2 Endpoints Status...
✓ Phase 3 Endpoints Status...

═══════════════════════════════════════════════════════════════════════════════
SYSTEM CHECK SUMMARY
═══════════════════════════════════════════════════════════════════════════════

Total Checks: 21/21

✓ SYSTEM VERIFIED - All checks passed!

Report saved to: system_check_report.json
```

---

## Step 3: Review the Detailed Report
```bash
# View JSON report
type system_check_report.json

# Or Pretty Print
python -m json.tool system_check_report.json
```

**Report includes:**
- ✅ Timestamp of execution
- ✅ Status: SYSTEM_VERIFIED / SYSTEM_OPERATIONAL / SYSTEM_ISSUES
- ✅ Pass rate percentage
- ✅ Details for each test module
- ✅ Individual test results

---

## Step 4: If Issues Found - Troubleshoot

### Issue: MongoDB Connection Failed
```bash
# Check if MongoDB is running
# Try connecting with MongoDB Compass
# Verify MONGO_URI is correct in .env or environment
```

### Issue: FastAPI Not Responding
```bash
# Start the backend
cd backend
python main.py

# In another terminal, run system check
python system_check.py
```

### Issue: Seed Data Missing
```bash
# Seed test data
python seed_phase2_3.py

# Then run system check again
python system_check.py
```

### Issue: Collections Don't Exist
```bash
# They'll be created automatically when first accessed
# Or manually seed first: python seed_phase2_3.py
```

---

## Step 5: Interpret Results

### Status Meanings

#### ✅ SYSTEM_VERIFIED
```
✓ All 21+ tests passed
✓ Pass rate: 100%
→ Safe for production deployment
→ No action needed
```

#### ⚠️ SYSTEM_OPERATIONAL
```
✓ 18-20 tests passed
✓ Pass rate: 85-99%
→ System operational with minor issues
→ Review warnings before deployment
→ Address non-critical issues if possible
```

#### ✗ SYSTEM_ISSUES
```
✓ Less than 18 tests passed
✓ Pass rate: < 85%
→ Critical issues detected
→ DO NOT deploy to production
→ Fix failures before proceeding
```

---

## Step 6: Generate Reports for SGP Documentation

### Create Test Summary for SGP
```markdown
# EduPath Optimizer - System Verification Results

**Date:** April 9, 2026
**Status:** ✅ SYSTEM VERIFIED
**Pass Rate:** 21/21 (100%)

## Test Results by Module

**Module 1: Connectivity** ✅ PASSED
- FastAPI: Operational
- MongoDB: Connected
- Collections: All 5 exist
- Indexes: All created
- Holidays: Configured

**Module 2: Logic** ✅ PASSED
- Attendance Math: Correct
- Date Filtering: Working
- Critical Risk: Triggered correctly
- Date Format: DD-MM-YYYY

**Module 3: Security** ✅ PASSED
- JWT: Generated
- RBAC: Enforced
- Teacher Access: Granted
- Student Access: Restricted

**Module 4: Phase 2 & 3** ✅ PASSED
- Academic Performance: Schema valid
- Curriculum Mapping: Linked
- Endpoints: Functional
- UI Components: Displayed
- Seed Data: 10 records

## Recommendation
System is ready for production deployment.
```

---

## Automated Testing Schedule

### For Development Environment
```bash
# Run after every major code change
python system_check.py

# Run before pushing to Git
python system_check.py

# Run before each Sprint review
python system_check.py
```

### For Staging Environment
```bash
# Run once per day
# Running time: ~15 seconds
python system_check.py

# Store reports with timestamps
python system_check.py > logs/system_check_$(date +%Y%m%d_%H%M%S).log
```

### For Production Environment
```bash
# Run before deployment
# Run after deployment
# Run monthly for health check
python system_check.py
```

---

## Extended Testing

### Manual Verification
Follow the checklist in `SYSTEM_VERIFICATION_CHECKLIST.md` for:
- Edge case testing
- UI interaction testing
- User workflow testing
- Data accuracy verification

### Test Data Verification
```bash
# Check seeded data exists
mongo
> use edupath_optimizer
> db.academic_performance.find()
> db.curriculum_map.find()

# Should return:
# - 10 academic performance records
# - 6 curriculum mappings
# - Valid mark ranges
```

### API Endpoint Testing
```bash
# Test Phase 2 endpoint
curl http://localhost:8000/api/phase-2-3/exam-strategy/2024001

# Test Phase 3 endpoint
curl http://localhost:8000/api/phase-2-3/bridge-report/2024001

# Test CSV Upload
curl -X POST "http://localhost:8000/api/teachers/upload-marks/csv?subject_code=CS101" \
  -F "file=@marks.csv"
```

---

## Performance Profiling

### Optional: Add Timing
Edit `system_check.py` to add timing info:

```python
import time

async def timed_check(name, func):
    start = time.time()
    result = await func()
    duration = time.time() - start
    print(f"{name}: {duration:.3f}s")
    return result
```

---

## CI/CD Integration

### For GitHub Actions
```yaml
name: System Check
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r backend/requirements.txt
      - name: Run system check
        run: python system_check.py
```

---

## Output Files Generated

After running `python system_check.py`:

1. **system_check_report.json**
   - JSON format report
   - Includes all test results
   - Timestamp of execution
   - Machine-readable format

2. **Console Output**
   - Color-coded pass/fail indicators
   - Human-readable summary
   - Quick status overview

---

## Troubleshooting the Script Itself

### Script Error: ImportError
```bash
# Ensure all dependencies installed
pip install motor pymongo pydantic fastapi requests holidays
```

### Script Error: Connection Refused
```bash
# Verify FastAPI is running
python backend/main.py &

# Verify MongoDB is running
# Then retry system check
python system_check.py
```

### Script Timeout
```bash
# Some tests might take longer if DB is under load
# Give it 30-60 seconds maximum
# If still timing out, check MongoDB performance
```

---

## Next Steps After Verification

✅ **If SYSTEM_VERIFIED:**
- Document results
- Create SGP report
- Plan deployment
- Schedule user training
- Deploy to production

⚠️ **If SYSTEM_OPERATIONAL:**
- Review warnings
- Fix non-critical issues
- Rerun verification
- Then deploy

✗ **If SYSTEM_ISSUES:**
- Review failures
- Fix critical issues
- Reseed data if needed
- Add missing configurations
- Rerun verification
- Debug specific failures

---

## Quick Reference

```bash
# Full system check
python system_check.py

# Just check connectivity
# (Modify system_check.py to run Module 1 only)

# Reseed test data
python seed_phase2_3.py

# View report
cat system_check_report.json

# Pretty print report
python -m json.tool system_check_report.json

# Check specific collection
mongo --eval "use edupath_optimizer; db.academic_performance.count()"
```

---

## Success Indicators

### When You See These → System is Good ✅

```
✓ SYSTEM VERIFIED - All checks passed!
✓ Total Checks: 21/21
✓ Pass rate shown as 100%
✓ All modules showing "PASSED"
✓ Database connected
✓ Collections present
✓ APIs responding
✓ No errors in output
```

### When You See These → Investigate ⚠️

```
⚠ SYSTEM OPERATIONAL
⚠ Pass rate 85-99%
⚠ Some collections empty (warnings)
⚠ Some endpoints not found (expected if not deployed yet)
```

### When You See These → Fix Issues ✗

```
✗ SYSTEM ISSUES
✗ Connection refused
✗ Collections missing
✗ KeyError exceptions
✗ MongoDB not accessible
```

---

## Support

For issues with system_check.py:
1. Check MongoDB is running
2. Check FastAPI is running  
3. Check all dependencies installed
4. Review SYSTEM_VERIFICATION_CHECKLIST.md
5. Check troubleshooting table in checklist

---

**Ready to verify your system? Run:**
```bash
python system_check.py
```

**Good luck! 🚀**
