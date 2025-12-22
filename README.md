# 🎓 EduPath Optimizer
> **An AI-Driven Strategic Attendance Suggestion System**

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-05998b.svg?logo=fastapi&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248.svg?logo=mongodb&logoColor=white)
![Status](https://img.shields.io/badge/Status-Day_3_Completed-success.svg)

## 🌟 Overview
**EduPath Optimizer** is not just an attendance tracker; it's a strategic academic assistant. It helps students maintain their 75% criteria by prioritizing lectures that align with their **Career Tracks** (Data Science, Cyber Security, etc.) while automatically accounting for public holidays and university events.

### 🚀 Key Features (Phase 1)
- [x] **Smart Calendar:** Automated public holiday fetching via Regional APIs.
- [x] **Weekend Logic:** Intelligent filtering of non-instructional days.
- [x] **Gap Analysis:** Real-time calculation of "Minimum Days to Attend" for target %.
- [x] **Pydantic Guard:** Robust data validation for zero-crash performance.
- [ ] **Career Prioritization:** (In Progress) Highlighting critical lectures for professional growth.

---

## 📊 Development Roadmap (Gantt Chart)
```mermaid
gantt
    title EduPath Optimizer Sprint Timeline
    dateFormat  YYYY-MM-DD
    section Phase 1: Core Logic
    Project Setup & API Setup           :done, d1, 2025-12-22, 1d
    Holiday & Weekend Filtering         :done, d2, 2025-12-22, 1d
    75% Gap Logic & Pydantic Refactor   :done, d3, 2025-12-22, 1d
    Career Track Dictionary Logic       :active, d4, 2025-12-23, 1d
    Weekly Timetable Mock Setup         :d5, 2025-12-24, 1d
    
    section Phase 2: Intelligence
    MongoDB Integration                 :d6, 2025-12-26, 3d
    End-Sem Diagnostic Strategy         :d7, 2026-01-05, 5d

    section Phase 3: Bridge
    Cumulative Academic Bridge          :d8, 2026-01-15, 5d