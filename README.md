# 🎓 EduPath Optimizer
> **An AI-Driven Strategic Attendance Suggestion System for University Students.**

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.127.0-05998b.svg?logo=fastapi&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248.svg?logo=mongodb&logoColor=white)
![Status](https://img.shields.io/badge/Status-Day_3_Completed-success.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**EduPath Optimizer** is an intelligent academic assistant that transitions from a simple attendance calculator into a diagnostic mentor. It helps students maintain their 75% attendance criteria while prioritizing lectures that align with their **Career Tracks** (Data Science, IOT, etc.) and identifying knowledge gaps across semesters.

---

## 🌟 Key Features
### 📅 Phase 1: Attendance Core (In Progress)
- [x] **Automated Holiday Fetching:** Integrated with `holidays` API to skip public holidays.
- [x] **Weekend Logic:** Intelligent filtering of non-instructional days (Sat/Sun).
- [x] **75% Gap Analysis:** Calculates the exact number of future classes required to stay safe.
- [x] **Pydantic Validation:** Industrial-grade data validation for robust performance.
- [ ] **Career Prioritization:** Algorithms to suggest dates based on professional interests.

### 🧠 Phase 2: End-Sem Strategy
- [ ] **CIE + Attendance Analysis:** Combines mid-term marks with attendance to predict exam risk.
- [ ] **Stress Ranking:** Identifies "Double Danger" subjects (Low marks + Low attendance).

### 🔗 Phase 3: Academic Bridge
- [ ] **Knowledge Gap Detection:** Links last semester's Uni Exam results to current prerequisites.
- [ ] **Foundation Planning:** Recommends bridge-courses for subjects where the student lacked foundation.

---

## 📊 Development Roadmap (Gantt Chart)

```mermaid
gantt
    title EduPath Optimizer Daily Sprint Schedule
    dateFormat  YYYY-MM-DD
    section Week 1: Core Logic
    Project Setup & API Setup           :done, d1, 2025-12-22, 1d
    Holiday & Weekend Filtering         :done, d2, 2025-12-22, 1d
    75% Gap Logic & Pydantic Refactor   :done, d3, 2025-12-22, 1d
    Career Track Dictionary Logic       :active, d4, 2025-12-23, 1d
    Weekly Timetable Mock Setup         :d5, 2025-12-24, 1d
    Saturday Logic Integration          :d6, 2025-12-27, 1d
    
    section Week 2: Database Layer
    MongoDB Atlas Setup                 :d7, 2025-12-29, 1d
    Connect FastAPI to Motor            :d8, 2025-12-30, 1d
    Student Profile CRUD                :d9, 2026-01-01, 1d
    Career Mapping in DB                :d10, 2026-01-02, 1d
    Saturday DB Integration             :d11, 2026-01-03, 1d

    section Week 3 & 4: UI & Final
    Frontend Dashboard (Tailwind)       :d12, 2026-01-05, 5d
    Logic & UI Integration              :d13, 2026-01-10, 5d
    Final SGP Demo & Documentation      :d14, 2026-01-15, 3d
```

## 📊 Day-to-Day Development Progress
```mermaid
gantt
    title EduPath Optimizer - Daily Sprint Schedule
    dateFormat  YYYY-MM-DD
    section Week 1: Core Logic
    Project Setup & FastAPI Setup     :done, d1, 2025-12-22, 1d
    Public Holiday API Integration    :done, d2, 2025-12-22, 1d
    Weekend Filtering Logic           :done, d3, 2025-12-22, 1d
    75% Attendance Gap Calculation    :done, d4, 2025-12-22, 1d
    Pydantic Validation & Refactoring :active, d5, 2025-12-23, 1d
    Career Track Dictionary Logic     :d6, 2025-12-24, 1d
    Weekly Timetable Mock Setup       :d7, 2025-12-25, 1d
```


## 🛠️ Tech Stack
- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Database:** [MongoDB Atlas](https://www.mongodb.com/atlas)
- **Validation:** [Pydantic v2](https://docs.pydantic.dev/)
- **API:** [Python-Holidays](https://pypi.org/project/holidays/)
- **Frontend:** HTML5, Tailwind CSS, JavaScript

---

## 🧠 Future Roadmap
### Phase 2: End-Sem Strategy
- [ ] **CIE + Attendance Analysis:** Combines mid-term marks with attendance to predict exam risk.
- [ ] **Stress Ranking:** Identifies "Double Danger" subjects (Low marks + Low attendance).

### Phase 3: Academic Bridge
- [ ] **Knowledge Gap Detection:** Links last semester's Uni Exam results to current prerequisites.
- [ ] **Foundation Planning:** Recommends bridge-courses for subjects where the student lacked foundation.

---

## ⚙️ Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/EduPath-Optimizer.git
   cd EduPath-Optimizer
   ```
## ⚙️ Setup
1. **Venv:** `python -m venv venv`
2. **Activate:** `.\venv\Scripts\activate` (Win) or `source venv/bin/activate` (Mac)
3. **Install:** `pip install fastapi uvicorn holidays`
4. **Run:** `uvicorn main:app --reload`

---
## 👨‍💻 Author
**Chaitany Thakar**
*SGP Project - University Attendance Optimizer*
