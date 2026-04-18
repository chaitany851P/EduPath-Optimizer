@echo off
title EduPath Optimizer - Professional Deployment

echo ------------------------------------------------
echo 🚀 Starting EduPath Optimizer Deployment...
echo ------------------------------------------------

:: 1. Install dependencies
echo 📦 Step 1: Installing dependencies...
pip install -r requirements.txt --quiet

:: 2. Seed database
echo 🌱 Step 2: Seeding database with test users...
python seed_users.py

if exist "seed_phase2_3.py" (
    echo 🌱 Step 3: Seeding Academic Performance...
    python seed_phase2_3.py
)

:: 3. Run server
echo.
echo ✅ Setup Complete!
echo 🌐 Server starting on http://localhost:8000
echo 👉 Access the Student Portal at: http://localhost:8000/student.html
echo ------------------------------------------------

cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
