# 🌐 WEB SYSTEM TESTING GUIDE
## EduPath Optimizer - Complete Backend & Frontend Testing

**Status:** Both Backend API and Web Frontend Ready for Testing
**Last Updated:** 2026-04-09

---

## 📋 QUICK SYSTEM STATUS CHECK

### Backend Components ✅
- **FastAPI Server**: `backend/main.py` - Ready
- **MongoDB Connection**: `database.py` - Configured
- **API Routes**: 6 router modules configured
- **Authentication**: JWT + OAuth2 implemented
- **CORS Enabled**: All origins allowed for development

### Frontend Components ✅
- **HTML Templates**: 6 templates ready (5 core + login)
- **CSS Styling**: Tailwind + custom styling
- **JavaScript**: Integrated for form handling
- **Responsive Design**: Mobile-friendly layout
- **Local Storage**: Session management

### Database ✅
- **MongoDB Atlas**: Connected
- **Collections**: 8+ collections available
- **Authentication**: API key configured

---

## 🚀 STARTUP PROCEDURES

### Option 1: Run Backend Only (API Development)

```bash
# 1. Navigate to backend directory
cd backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the API server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Expected output:
# ✓ Uvicorn running on http://127.0.0.1:8000
# ✓ API docs available at http://127.0.0.1:8000/docs
# ✓ ReDoc available at http://127.0.0.1:8000/redoc
```

### Option 2: Run Full Web Application (API + Frontend)

```bash
# 1. Navigate to project root
cd e:\SGP\EduPath_Optimizer

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the main application
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Expected output:
# ✓ Uvicorn running on http://127.0.0.1:8000
# ✓ Web interface available at http://127.0.0.1:8000
```

### Option 3: Using Docker (Production-Like)

```bash
# 1. Build and start with Docker Compose
docker-compose up -d

# OR with Podman
podman-compose up -d

# 2. Check status
docker-compose ps

# 3. Initialize database (if needed)
docker-compose exec api python backend/init_db.py

# 4. Access services:
# - Main App: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Database: localhost:27017
```

---

## 🧪 TESTING PROCEDURES

### PART 1: BACKEND API TESTING

#### Test 1.1: Health Check Endpoints

```bash
# Simple ping test
curl http://localhost:8000/health

# Expected Response:
# {"status": "healthy"}
```

#### Test 1.2: API Documentation

```
# Visit in browser:
http://localhost:8000/docs

# Or for ReDoc:
http://localhost:8000/redoc

# You should see:
✓ All 6 API route groups listed
✓ Expandable route endpoints
✓ Request/Response schemas
✓ Try it out functionality
```

#### Test 1.3: Root Endpoint

```bash
curl http://localhost:8000/

# Expected Response:
# {"message": "EduPath Optimizer API is running (Phase 1-3)", "version": "2.0.0"}
```

#### Test 1.4: Student Routes Testing

```bash
# Get all students
curl http://localhost:8000/api/students/

# Expected: List of students or empty array []

# Create a test student
curl -X POST http://localhost:8000/api/students/ \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "TEST_2024_001",
    "name": "Test Student",
    "email": "test@university.edu",
    "branch": "CSE",
    "semester": 4
  }'

# Expected: Student created with ID

# Get specific student
curl http://localhost:8000/api/students/TEST_2024_001

# Expected: Student details with all fields
```

#### Test 1.5: Attendance Routes Testing

```bash
# Mark attendance
curl -X POST http://localhost:8000/api/attendance/ \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "TEST_2024_001",
    "subject_code": "CS101",
    "date": "2026-04-09",
    "attended": true
  }'

# Get attendance record
curl http://localhost:8000/api/attendance/TEST_2024_001

# Expected: Attendance records for the student
```

#### Test 1.6: Phase 2-3 Routes Testing

```bash
# Get exam readiness (Double Danger Rule)
curl http://localhost:8000/api/phase-2-3/exam-readiness/TEST_2024_001

# Expected: Exam risk assessment with priority scores

# Get academic bridge info (Prerequisites)
curl http://localhost:8000/api/phase-2-3/academic-bridge/TEST_2024_001

# Expected: Prerequisite gaps and severity levels
```

#### Test 1.7: Admin Routes Testing

```bash
# Get dashboard stats
curl http://localhost:8000/api/admin/dashboard/

# Expected: Overall statistics and metrics

# Batch student upload
curl -X POST http://localhost:8000/api/admin/bulk-students/ \
  -F "file=@students.csv"

# Expected: Upload confirmation
```

---

### PART 2: FRONTEND WEB TESTING

#### Test 2.1: Access Web Application

```
Open Browser and navigate to:
http://localhost:8000

Expected Result:
✓ Login page appears
✓ Navigation elements visible
✓ Styling looks professional (blue & white theme)
✓ No console errors (press F12 to check)
```

#### Test 2.2: Login Page Testing

```
1. Click "Login" button
2. Try entering credentials:
   - Email: test@university.edu
   - Password: testpass123

Expected Behavior:
✓ Form validates input
✓ Error/success message appears
✓ On success: redirects to dashboard
✓ On failure: shows error clearly
```

#### Test 2.3: Student Dashboard Features

After login as student:

```
Dashboard should show:
✓ Tab 1: ATTENDANCE STATUS
  - Current attendance percentage
  - Classes attended vs missed
  - Target attendance (75%)
  - Days to semester end
  
✓ Tab 2: EXAM READINESS (Phase 2)
  - Double Danger Rule indicator
  - Risk level (SAFE/WARNING/CRITICAL)
  - Subject-wise marks
  - Priority scores
  
✓ Tab 3: FOUNDATION CHECK (Phase 3)
  - Prerequisite gaps detected
  - Recommended refresher topics
  - 5-day action plan
  - Severity levels per subject
```

#### Test 2.4: Forms and Data Entry

Test student profile update:
```
1. Navigate to "Settings" or "Profile"
2. Update fields:
   - Phone number
   - Address
   - Career preference
3. Click "Save"

Expected:
✓ Form validates (email format, phone digits, etc.)
✓ Success message appears
✓ Data persists after page refresh
✓ No errors in browser console
```

#### Test 2.5: Teacher Interface Testing

If teacher login available:
```
Teacher dashboard should show:
✓ Attendance marking interface
✓ Bulk upload capability
✓ Mark entry forms
✓ Student performance reports
✓ Class statistics
```

#### Test 2.6: Admin Panel Testing

If admin login available:
```
Admin dashboard should show:
✓ System statistics (total students, subjects, etc)
✓ Recent activities log
✓ User management
✓ System settings
✓ Reports and exports
```

#### Test 2.7: Responsive Design Testing

```
Test on different screen sizes:

Desktop (1920x1080):
✓ Full layout displays correctly
✓ Sidebar visible on left
✓ Content flows properly
✓ No horizontal scrolling

Tablet (768x1024):
✓ Responsive adjustments applied
✓ Sidebar may collapse to menu icon
✓ Touch-friendly buttons

Mobile (375x667):
✓ Mobile menu navigation works
✓ Stack layout applied
✓ Touch interactions work
✓ No overlapping elements
```

---

## 🔍 API ENDPOINT REFERENCE

### Core Endpoints

| Method | Endpoint | Purpose | Status |
|--------|----------|---------|--------|
| GET | `/` | Root endpoint | ✅ |
| GET | `/health` | Health check | ✅ |
| GET | `/docs` | Swagger UI | ✅ |
| GET | `/redoc` | ReDoc docs | ✅ |

### Student Routes (`/api/students`)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | List all students |
| GET | `/{student_id}` | Get specific student |
| POST | `/` | Create new student |
| PUT | `/{student_id}` | Update student |
| DELETE | `/{student_id}` | Delete student |

### Attendance Routes (`/api/attendance`)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/{student_id}` | Get attendance records |
| POST | `/` | Mark attendance |
| GET | `/{student_id}/summary` | Attendance summary |
| GET | `/{student_id}/percentage` | Calculate percentage |

### Phase 2-3 Routes (`/api/phase-2-3`)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/exam-readiness/{student_id}` | Exam risk assessment |
| GET | `/academic-bridge/{student_id}` | Prerequisite gaps |
| POST | `/mark-upload` | Upload marks |
| GET | `/priority-list` | Prioritized students |

### Admin Routes (`/api/admin`)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/dashboard` | Dashboard stats |
| POST | `/bulk-students` | Bulk upload |
| POST | `/bulk-marks` | Bulk marks upload |
| GET | `/reports` | Generate reports |

---

## 🐛 COMMON ISSUES & TROUBLESHOOTING

### Issue 1: MongoDB Connection Failed
```
Error: "Unable to connect to MongoDB"

Solution:
✓ Check internet connection
✓ Verify MongoDB Atlas credentials in config
✓ Check IP whitelist in MongoDB Atlas
✓ Verify database URL is correct
```

### Issue 2: CORS Errors in Console
```
Error: "Access to XMLHttpRequest blocked by CORS policy"

Solution:
✓ CORS is already enabled in main.py
✓ Check if backend is running
✓ Clear browser cache (Ctrl+Shift+Delete)
✓ Check console for specific error details
```

### Issue 3: Templates Not Found
```
Error: "TemplateNotFound: login.html"

Solution:
✓ Verify templates/ folder exists in project root
✓ Check file names are correct:
  - admin.html
  - index.html
  - login.html
  - student.html
  - teacher.html
✓ Restart server after verifying paths
```

### Issue 4: Static Files Not Loading
```
Error: CSS/JS not applying, 404 in console

Solution:
✓ Ensure backend/static/ folder exists (if used)
✓ Check CSS @import statements in HTML
✓ Use browser DevTools to find 404 resources
✓ Verify file paths are relative or absolute correctly
```

### Issue 5: Port Already in Use
```
Error: "OSError: [Errno 48] Address already in use"

Solution:
# Kill process using port 8000
Windows:
  netstat -ano | findstr :8000
  taskkill /PID <PID> /F

macOS/Linux:
  lsof -i :8000
  kill -9 <PID>

# Or use different port:
python -m uvicorn main:app --port 8001
```

### Issue 6: 404 Not Found on Root Path
```
Error: "GET / returns 404"

Solution:
✓ Check main.py has a root route handler
✓ Verify TemplateResponse is correctly configured
✓ Check static HTML files exist in templates/
✓ Ensure app.mount() is called for static files if needed
```

---

## ✅ VALIDATION CHECKLIST

### Backend API Status
- [ ] Server starts without errors
- [ ] Health endpoint responds (200)
- [ ] API docs available at /docs
- [ ] All 6 route groups loaded
- [ ] Can create student via POST
- [ ] Can retrieve student via GET
- [ ] Can mark attendance
- [ ] Can get exam readiness
- [ ] Phase 2-3 endpoints working
- [ ] MongoDB connection successful

### Frontend Web Status
- [ ] Login page loads and displays
- [ ] Navigation elements visible
- [ ] Styling applied correctly (blue theme)
- [ ] Forms are responsive
- [ ] Can submit login form
- [ ] Dashboard shows after login
- [ ] Tabs functional (Attendance, Exam, Foundation)
- [ ] Data persists in browser storage
- [ ] Mobile responsive (test on DevTools)
- [ ] No errors in browser console (F12)

### Data Operations
- [ ] Create new student works
- [ ] Read student data works
- [ ] Update student profile works
- [ ] Mark attendance successfully
- [ ] Calculate attendance percentage accurately
- [ ] Detect Double Danger Rule correctly
- [ ] Identify prerequisite gaps
- [ ] Generate action plans
- [ ] Store data in MongoDB

### Performance
- [ ] Page loads under 3 seconds
- [ ] API responses under 500ms
- [ ] No memory leaks (check DevTools)
- [ ] Handles 100+ concurrent users
- [ ] Database queries optimized

---

## 📊 EXPECTED TEST RESULTS

### Phase 1: Attendance Optimization
```
Test Input:
- Student: 2024001
- Classes attended: 30 out of 40
- Attendance: 75%
- Missing classes: 10

Expected Output:
✅ Attendance: 75% (meets requirement)
✅ Status: SAFE - at target
✅ Days remaining: Calculated correctly
✅ Optimization: Not needed (already at 75%)
```

### Phase 2: Exam Strategy (Double Danger Rule)
```
Test Input:
- Attendance: 74% (< 75%)
- Marks: 48% (< 50%)

Expected Output:
✅ Status: CRITICAL 🔴
✅ Action: Double Danger Rule Triggered
✅ Recommendation: Immediate intervention
✅ Priority Score: High
```

### Phase 3: Academic Bridge
```
Test Input:
- Current Subject: Advanced DS
- Prerequisite: Basic DS (60% marks - MEDIUM gap)

Expected Output:
✅ Gap Detected: Yes
✅ Severity: MEDIUM
✅ 5-Day Plan: Generated
✅ Topics: Listed with daily breakdown
```

---

## 🎯 SUCCESS CRITERIA

### Functionality ✅
- [ ] All 48 edge case tests pass
- [ ] Backend API returns correct responses
- [ ] Frontend displays data correctly
- [ ] Forms validate and submit properly
- [ ] Phase 1-3 logic executes correctly

### Performance ✅
- [ ] Page load time < 3 seconds
- [ ] API response time < 500ms
- [ ] Database queries < 1 second
- [ ] No console errors
- [ ] Handles 1000+ students efficiently

### User Experience ✅
- [ ] Login flow works smoothly
- [ ] Dashboard is intuitive
- [ ] Mobile responsive
- [ ] Error messages clear
- [ ] Success feedback provided

### Data Integrity ✅
- [ ] Data persists correctly
- [ ] MongoDB stores all required fields
- [ ] No data corruption
- [ ] Transaction consistency
- [ ] Backup/recovery works

---

## 📝 TEST LOG TEMPLATE

```
TEST DATE: 2026-04-09
TESTER: [Your Name]
ENVIRONMENT: Development

BACKEND TESTS
─────────────────────────────
Health Check: ✅ PASS / ❌ FAIL
API Docs: ✅ PASS / ❌ FAIL
Student Routes: ✅ PASS / ❌ FAIL
Attendance Marking: ✅ PASS / ❌ FAIL
Phase 2-3 Logic: ✅ PASS / ❌ FAIL
Admin Functions: ✅ PASS / ❌ FAIL

FRONTEND TESTS
─────────────────────────────
Login Page: ✅ PASS / ❌ FAIL
Dashboard: ✅ PASS / ❌ FAIL
Attendance Tab: ✅ PASS / ❌ FAIL
Exam Tab: ✅ PASS / ❌ FAIL
Foundation Tab: ✅ PASS / ❌ FAIL
Responsive Design: ✅ PASS / ❌ FAIL

ISSUES FOUND
─────────────────────────────
1. [Issue description]
   Severity: Critical / High / Medium / Low
   Workaround: [If available]

2. [Issue description]
   Severity: Critical / High / Medium / Low
   Workaround: [If available]

OVERALL STATUS: ✅ READY / ⚠️ NEEDS FIXING / ❌ BLOCKED
```

---

## 🚀 NEXT STEPS

1. ✅ Run system diagnostics: `python system_check.py`
2. ⏳ Start backend server: `uvicorn backend/main:app --reload`
3. ⏳ Test API endpoints: Use Swagger at `/docs`
4. ⏳ Access web interface: Open `http://localhost:8000`
5. ⏳ Test all features: Use validation checklist
6. ⏳ Document issues: Fill test log
7. ⏳ Deploy to production: Follow deployment guide

---

## 📞 SUPPORT & DOCUMENTATION

**For Backend Issues:**
- Check `backend/main.py` - Main API setup
- Check `backend/routers/` - Individual route modules
- See `PRODUCTION_DEPLOYMENT_GUIDE.md`

**For Frontend Issues:**
- Check `templates/*.html` - HTML pages
- Check `templates/shared.css` - Styling
- See `QUICK_REFERENCE.md`

**For Database Issues:**
- See `backend/database.py` - Connection setup
- Check `backend/config.py` - Configuration
- See `backend/init_db.py` - Initialization

**For Deployment Issues:**
- Follow `PRODUCTION_DEPLOYMENT_GUIDE.md`
- Or use Docker: `docker-compose up -d`
- Or Podman: `podman-compose up -d`

---

**Status: ✅ READY FOR TESTING**
**Last Updated: 2026-04-09**
**Version: 1.0**
