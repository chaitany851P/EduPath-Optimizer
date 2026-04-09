# 🚀 EduPath Optimizer - Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying EduPath Optimizer as a production-ready university system with multi-campus and multi-department support.

---

## 📋 Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [Database Initialization](#database-initialization)
4. [Security Hardening](#security-hardening)
5. [Deployment Methods](#deployment-methods)
6. [Health Monitoring](#health-monitoring)
7. [Backup & Recovery](#backup--recovery)
8. [Troubleshooting](#troubleshooting)

---

## ✅ Pre-Deployment Checklist

### Prerequisites
- [ ] Python 3.8+ installed
- [ ] MongoDB Atlas account (or on-premises MongoDB server)
- [ ] Git repository configured
- [ ] SSL/TLS certificates ready
- [ ] SMTP server credentials (for email notifications)
- [ ] Sufficient disk space (minimum 2GB free)

### Code Preparation
- [ ] All tests passing (`pytest` or `python system_check.py`)
- [ ] Code merged into main branch
- [ ] Environment variable template created (`.env.example`)
- [ ] Database migration scripts tested
- [ ] API documentation generated

### Infrastructure Preparation
- [ ] DNS configured for domain
- [ ] Firewall rules configured
- [ ] Load balancer setup (if multi-server)
- [ ] Backup storage configured
- [ ] Monitoring tools installed

---

## 🔧 Environment Setup

### Step 1: Create Production `.env` File

```bash
# Copy template
cp .env.example .env

# Edit with production values
nano .env
```

### Essential Production Settings

```env
# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Security (CRITICAL)
SECRET_KEY=<generate-strong-key>  # Use: python -c "import secrets; print(secrets.token_urlsafe(32))"
ALGORITHM=HS256

# MongoDB (Cloud or On-Premises)
MONGODB_URI=mongodb+srv://prod_user:strong_password@prod-cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=edupath_optimizer_prod

# University Configuration
UNIVERSITY_NAME=Your University Official Name
UNIVERSITY_ID=UNIV_001
ENABLE_MULTI_CAMPUS=true
DEFAULT_CAMPUS_ID=CAMPUS_MAIN

# Security Settings
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=https://your-domain.edu,https://www.your-domain.edu

# Email (if notifications enabled)
EMAIL_ENABLED=true
SMTP_SERVER=smtp.outlook.office365.com
SMTP_PORT=587
SMTP_USER=notifications@your-domain.edu
SMTP_PASSWORD=<app-password>
SENDER_EMAIL=notifications@your-domain.edu

# Backup Configuration
ENABLE_BACKUPS=true
BACKUP_FREQUENCY=daily
BACKUP_RETENTION_DAYS=30
BACKUP_LOCATION=/var/backups/edupath

# Monitoring
ENABLE_METRICS=true
ENABLE_SENTRY=true
SENTRY_DSN=<your-sentry-dsn>
SENTRY_ENVIRONMENT=production
```

### Step 2: Verify Configuration

```bash
# Test configuration loading
python -c "from backend.config import settings; settings.print_config_summary()"
```

---

## 💾 Database Initialization

### Method 1: Automated Initialization (Recommended)

```bash
# Navigate to project root
cd /path/to/EduPath_Optimizer

# Run initialization script
python backend/init_db.py
```

**Expected Output:**
```
✓ MongoDB connection successful
✓ Creating collections...
✓ Created collection: students
✓ Creating indexes...
✓ Initialized campuses...
✓ Database initialized successfully! ✓
Status: READY FOR DEPLOYMENT ✓
```

### Method 2: Manual Initialization

```python
import asyncio
from backend.database import init_db

# Run initialization
asyncio.run(init_db())
```

### Verify Database

```bash
# Check health
curl http://localhost:8000/api/health/full

# Expected Response:
# {
#   "status": "healthy",
#   "database": { "status": "healthy", "connected": true },
#   "collections_stats": { "students": 0, "subjects": 0, ... }
# }
```

---

## 🔐 Security Hardening

### 1. HTTPS/SSL Configuration

**Using Nginx (Recommended)**

```nginx
# /etc/nginx/sites-available/edupath
upstream edupath_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.edu;
    return 301 https://$server_name$request_uri;  # Redirect to HTTPS
}

server {
    listen 443 ssl http2;
    server_name your-domain.edu;

    ssl_certificate /etc/ssl/certs/your-cert.crt;
    ssl_certificate_key /etc/ssl/private/your-key.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://edupath_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. Database Security

```bash
# Create MongoDB user with limited permissions
# In MongoDB shell:
db.createUser({
  user: "edupath_user",
  pwd: "strong_password_here",
  roles: [
    { role: "readWrite", db: "edupath_optimizer_prod" },
    { role: "dbOwner", db: "edupath_optimizer_prod" }
  ]
})
```

### 3. API Security

- [ ] Enable rate limiting (Nginx/HAProxy)
- [ ] Implement CORS properly (configured in `config.py`)
- [ ] Enforce HTTPS only
- [ ] Set secure headers
- [ ] Enable API key authentication (optional)
- [ ] Implement request validation
- [ ] Set up IP whitelisting for admin endpoints

### 4. Authentication Security

```env
# Use strong JWT secrets
SECRET_KEY=<min-32-character-random-string>
ACCESS_TOKEN_EXPIRE_MINUTES=60  # Shorter in production
REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

## 🚀 Deployment Methods

### Method 1: Systemd Service (Linux)

```bash
# Create service file
sudo nano /etc/systemd/system/edupath.service
```

```ini
[Unit]
Description=EduPath Optimizer Production Server
After=network.target

[Service]
Type=notify
User=edupath
WorkingDirectory=/opt/edupath
Environment="PATH=/opt/edupath/venv/bin"
ExecStart=/opt/edupath/venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable edupath
sudo systemctl start edupath
sudo systemctl status edupath
```

### Method 2: Docker Deployment (Recommended for Scalability)

```bash
# See DOCKER_DEPLOYMENT.md for complete Docker setup
docker-compose -f docker-compose.prod.yml up -d
```

### Method 3: Cloud Deployment

**AWS EC2:**
```bash
# Launch security group with ports 22, 80, 443 open
# Install dependencies, clone repo, run init_db.py, start with systemd
```

**Azure App Service:**
```bash
# Create app service, connect to Git, environment variables in app settings
az webapp create --resource-group <group> --plan <plan> --name <name>
```

---

## 📊 Health Monitoring

### Endpoints for Monitoring

```bash
# Ping endpoint (uptime checks)
curl http://your-domain.edu/api/health/ping

# Liveness probe (Docker/Kubernetes)
curl http://your-domain.edu/api/health/live

# Readiness probe (ready to handle traffic)
curl http://your-domain.edu/api/health/ready

# Full health check
curl http://your-domain.edu/api/health/full

# System metrics
curl http://your-domain.edu/api/health/metrics

# Capacity check
curl http://your-domain.edu/api/health/capacity

# Status page
curl http://your-domain.edu/api/health/status-page
```

### Monitoring Setup

**Prometheus Config** (`prometheus.yml`):
```yaml
scrape_configs:
  - job_name: 'edupath'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:9090']
```

**Grafana Dashboard:**
- Import JSON dashboard
- Configure Prometheus data source
- Set up alerts for:
  - Database connection failures
  - High CPU usage (>85%)
  - High memory usage (>85%)
  - Disk space low (<10%)

---

## 💾 Backup & Recovery

### Automated Backups

```bash
# Create backup directory
sudo mkdir -p /var/backups/edupath
sudo chown edupath:edupath /var/backups/edupath

# Create backup script (/opt/edupath/backup.sh)
#!/bin/bash
BACKUP_DIR="/var/backups/edupath"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mongodump --uri="mongodb+srv://..." --out="$BACKUP_DIR/backup_$TIMESTAMP"

# Schedule via crontab (daily at 2 AM)
0 2 * * * /opt/edupath/backup.sh
```

### Disaster Recovery

```bash
# Restore from backup
mongorestore --uri="mongodb+srv://..." --dir="/var/backups/edupath/backup_20240409_020000"

# Verify restoration
python backend/init_db.py  # Verify indexes
curl http://localhost:8000/api/health/full  # Verify connectivity
```

---

## 🔍 Troubleshooting

### Issue: Database Connection Failed

**Solution:**
```bash
# 1. Verify credentials in .env
# 2. Check MongoDB Atlas IP whitelist
# 3. Test connection
mongo "mongodb+srv://user:password@cluster.mongodb.net/db"
# 4. Check firewall rules
sudo ufw allow 27017
```

### Issue: High Memory Usage

**Solution:**
```bash
# Check current usage
free -h

# Reduce workers if CPU is not bottleneck
# Edit systemd service or docker-compose
workers = 2  # Reduce from 4
```

### Issue: SSL Certificate Errors

**Solution:**
```bash
# Renew Let's Encrypt certificate
sudo certbot renew --dry-run
sudo systemctl restart nginx
```

### Issue: Slow API Responses

**Solution:**
```bash
# Check database performance
mongo # Enter MongoDB shell
db.collection.find().explain("executionStats")

# Verify indexes exist
python backend/init_db.py

# Check server resources
htop
```

---

## 📈 Performance Tuning

### MongoDB Optimization

```javascript
// Enable compression
db.collection.createIndex(...)

// Monitor slow queries
db.setProfilingLevel(1, {slowms: 100})
db.system.profile.find().sort({ts:-1}).limit(10)
```

### API Optimization

```python
# In backend/main.py
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend

# Enable caching for GET endpoints
@app.get('/cached-endpoint')
@cached(expire=300)
async def cached_endpoint():
    return {...}
```

---

## 📋 Post-Deployment

### Day 1 Validation

- [ ] All health checks passing
- [ ] Database backups working
- [ ] Email notifications functional
- [ ] Admin dashboard accessible
- [ ] Student/Teacher authentication working
- [ ] Phase 1/2/3 endpoints operational

### Week 1 Validation

- [ ] Monitor system logs for errors
- [ ] Verify backup restoration works
- [ ] Check user onboarding workflow
- [ ] Load test with 100+ concurrent users
- [ ] Verify data isolation (multi-campus)

### Ongoing Monitoring

- [ ] Daily health check reviews
- [ ] Weekly performance analysis
- [ ] Monthly security audits
- [ ] Quarterly disaster recovery drills

---

## 🎯 Success Criteria

✅ All endpoints respond < 200ms  
✅ Database < 80% capacity  
✅ Zero data corruption incidents  
✅ Email notifications functional  
✅ Backups completing daily  
✅ Multi-campus data properly segregated  
✅ All users authenticated and authorized  
✅ Phase 1, 2, 3 features operational  

---

## 📞 Support & Documentation

- **System Verification:** Run `python system_check.py`
- **Configuration:** See `backend/config.py`
- **API Documentation:** Visit `/docs` endpoint
- **Health Status:** Visit `/api/health/full`

---

**Status:** ✅ Production Ready  
**Version:** 2.0.0  
**Last Updated:** April 2026
