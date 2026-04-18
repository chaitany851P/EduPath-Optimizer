#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════════
# EduPath Optimizer - Quick Start Script
# ═══════════════════════════════════════════════════════════════════════════════

echo "------------------------------------------------"
echo "🚀 Starting EduPath Optimizer Deployment..."
echo "------------------------------------------------"

# 1. Install/Update dependencies
echo "📦 Step 1: Installing dependencies..."
pip install -r requirements.txt --quiet

# 2. Re-seed the database with professional test data
# Note: This ensures you have the latest hashing logic for logins
echo "🌱 Step 2: Seeding database with test users..."
python seed_users.py

# 3. Check for any other necessary seeds (Phase 2 & 3)
if [ -f "seed_phase2_3.py" ]; then
    echo "🌱 Step 3: Seeding Academic Performance & Curriculum Maps..."
    python seed_phase2_3.py
fi

# 4. Launch the Backend Server
# Running with --app-dir backend to ensure correct module resolution
echo ""
echo "✅ Setup Complete!"
echo "🌐 Server starting on http://localhost:8000"
echo "👉 Access the Student Portal at: http://localhost:8000/student.html"
echo "👉 Access the Admin Console at: http://localhost:8000/admin.html"
echo "------------------------------------------------"

cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
