# 🎓 EduPath Optimizer (V2.0)
> **Strategic AI-Driven Attendance & Academic Success System for Professional Growth.**

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Production_Ready-05998b.svg?logo=fastapi&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248.svg?logo=mongodb&logoColor=white)
![UI](https://img.shields.io/badge/UI-Bootstrap_5_Premium-purple.svg)
![Deployment](https://img.shields.io/badge/Deployment-Docker_Ready-blue.svg?logo=docker)

**EduPath Optimizer** is an enterprise-grade academic assistant that transforms from a simple attendance tracker into a high-intelligence diagnostic mentor. It helps university students hit the 75% attendance criteria while strategically prioritizing their career interests and identifying critical academic risks before final exams.

---

## 🚀 Key Modules (3-Phase Ecosystem)

### 📅 Phase 1: Strategic Attendance Roadmap
- **AI Holiday Engine:** Automatically filters public holidays (via API) and University Fests.
- **Career-First Logic:** Suggests dates for classes that match the student's track (AI/ML, Cyber Security, etc.) first.
- **The "Gap" Math:** Calculates exact working days remaining and mandatory attendance counts.
- **Impossible Target Detection:** Triggers a red alert if hitting 75% is mathematically impossible.

### 🧠 Phase 2: End-Sem Diagnostic (Double Danger)
- **Stress Score Algorithm:** Correlates Attendance + Internal Marks (CIE/Mid-term).
- **Double Danger Rule:** Flags subjects where the student has <70% attendance AND <40% marks as "CRITICAL RISK."
- **Study Time Allocation:** Generates a prioritized study list with specific time-weighting (e.g., "Allocate 40% of your time to Data Structures").

### 🔗 Phase 3: The Academic Bridge
- **Prerequisite Gap Detection:** Links last semester's results to current subjects.
- **Foundation Refresher:** Automatically suggests 5-day "Refresher Plans" for current subjects if foundations from past semesters were weak.

---

## 🛠️ Technical Architecture
- **Backend:** Modular FastAPI with independent routers for Auth, Admin, and Strategy.
- **Frontend:** Professional SPA (Single Page Application) built with **Bootstrap 5**, featuring smooth fade transitions and pulsing risk alerts.
- **Security:** Industry-standard JWT (JSON Web Tokens) with PBKDF2-HMAC-SHA256 salted hashing.
- **Database:** Asynchronous IOMotor with MongoDB Atlas.

---

## ⚙️ Quick Start (Deployment Ready)

### **Option 1: Windows (Recommended)**
Double-click **`run.bat`**. This will:
1. Install all dependencies.
2. Seed the database with professional test profiles.
3. Launch the server at `http://localhost:8000`.

### **Option 2: Linux/Mac/Git Bash**
Run the startup shell script:
```bash
chmod +x start.sh
./start.sh
```

### **Option 3: Docker**
The project is fully containerized:
```bash
docker-compose up --build
```

---

## 📋 Professional Test Credentials

| Role | Username | Password | Status |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | Full System Access |
| **Teacher** | `teacher01` | `teacher123` | Attendance Management |
| **Student (Risk)** | `2024001` | `student123` | Shows CRITICAL / DOUBLE DANGER |
| **Student (Safe)** | `2024003` | `student123` | Shows GOAL MET / SAFE |

---

## 📂 Project Structure
```text
├── backend/            # Core FastAPI Logic & Routers
├── templates/          # Professional Dashboard UI (HTML/CSS)
├── Dockerfile          # Production Container Config
├── run.bat             # Windows One-Click Start
├── start.sh            # Linux/Mac Startup
├── seed_users.py       # Database Initialization
└── system_check.py     # 360° Health Diagnostic
```

---
## 👨‍💻 Author
**Chaitany Thakar**
*Enterprise SGP Project - High-Intelligence University Success System*
