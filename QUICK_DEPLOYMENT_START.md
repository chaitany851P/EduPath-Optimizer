# 🎯 EduPath Optimizer - Quick Deployment Start

## For Development (5 minutes)

```bash
# 1. Install dependencies
pip install -r backend/requirements.txt

# 2. Create .env for development
cp .env.example .env
# Edit: Set ENVIRONMENT=development

# 3. Initialize database
python backend/init_db.py

# 4. Start server
python backend/main.py

# 5. Test
curl http://localhost:8000/api/health/ping
# Should return: {"status": "pong", ...}
```

---

## For Production with Docker (3 steps)

### Step 1: Prepare Configuration

```bash
# Create production .env
cat > .env << EOF
ENVIRONMENT=production
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
UNIVERSITY_NAME="Your University Name"
ENABLE_MULTI_CAMPUS=true
EOF
```

### Step 2: Build & Deploy

```bash
# Start all services (API + MongoDB + Nginx + Monitoring)
docker-compose up -d

# Initialize database
docker-compose exec api python backend/init_db.py

# Check health
curl http://localhost:8000/api/health/full
```

### Step 3: Verify Production Readiness

```bash
# All checks should pass ✅
docker-compose exec api python system_check.py

# Expected output: Status: ✓ SYSTEM VERIFIED - All checks passed!
```

---

## System Ready Indicators

✅ **Connectivity** - Database connected  
✅ **Logic** - All math checks pass  
✅ **RBAC** - Authentication working  
✅ **Phase 1-3** - All features operational  
✅ **Multi-Campus** - Data properly segregated  
✅ **Health** - All endpoints < 200ms response  

---

## Access Application

| Component | URL | Default Creds |
|-----------|-----|---|
| **API** | http://localhost:8000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **MongoDB** | mongodb://localhost:27017 | admin/changeme |
| **Prometheus** | http://localhost:9090 | - |
| **Grafana** | http://localhost:3000 | admin/admin |

---

## Key Endpoints

```bash
# Monitoring
curl http://localhost:8000/api/health/ping         # Uptime
curl http://localhost:8000/api/health/full        # Full health
curl http://localhost:8000/api/health/metrics     # Metrics
curl http://localhost:8000/api/health/capacity    # Resource usage
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| MongoDB won't connect | Check `.env` MONGODB_URI, verify IP whitelist in Atlas |
| Port 8000 already in use | Change PORT in `.env` or stop conflicting process |
| High memory usage | Reduce WORKERS in config, increase container memory |
| Build fails | Run `pip install --upgrade pip setuptools` first |

---

## Production Verification Checklist

- [ ] Database backups running daily
- [ ] Health checks passing (`/api/health/full`)
- [ ] Logs centralized and monitored
- [ ] HTTPS/SSL configured
- [ ] CORS properly restricted
- [ ] Email notifications functional
- [ ] Multi-campus data segregation verified
- [ ] Admin dashboard accessible
- [ ] Student/Teacher auth working

---

## Deployment Status

### Development
```bash
docker-compose up -d
# Includes: API + MongoDB + Prometheus + Grafana
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d
# Add: Nginx reverse proxy, SSL, backups
```

---

## Next Steps

1. ✅ Setup environment (`.env`)
2. ✅ Run initialization (`python backend/init_db.py`)
3. ✅ Start services (`docker-compose up -d`)
4. ✅ Run verification (`python system_check.py`)
5. ✅ Check health (`curl /api/health/full`)
6. ✅ Access docs (http://localhost:8000/docs)

---

**Ready to deploy? Start here:** 👇

```bash
# Development
docker-compose up -d && docker-compose exec api python backend/init_db.py

# Production
docker-compose -f docker-compose.prod.yml up -d && docker-compose exec api python backend/init_db.py
```

---

**Status:** ✅ Ready for Deployment  
**Version:** 2.0.0  
**Multi-Campus:** ✅ Enabled  
**Docker:** ✅ Supported  
