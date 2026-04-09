# 🚀 Podman Quick Start - 5 Minutes

## Install Podman

### Windows/Mac
```bash
# Download Podman Desktop from podman.io
# Or: brew install podman (macOS)
# Or: choco install podman (Windows with Chocolatey)

# After install, initialize:
podman machine init
podman machine start

# Verify
podman --version
podman run hello-world
```

### Linux
```bash
sudo apt-get update
sudo apt-get install -y podman podman-compose

# Verify
podman --version
podman run hello-world
```

---

## Deploy EduPath Optimizer (3 Steps)

### Step 1: Prepare (30 seconds)
```bash
cd /path/to/EduPath_Optimizer
cp .env.example .env
# Edit: MONGODB_URI, SECRET_KEY, UNIVERSITY_NAME
```

### Step 2: Start (1 minute)
```bash
# Build image
podman build -t edupath-optimizer:latest .

# Start all services
podman-compose up -d

# Expected: 5 services starting (api, mongodb, nginx, prometheus, grafana)
```

### Step 3: Verify (30 seconds)
```bash
# Check services
podman-compose ps

# Initialize database
podman-compose exec api python backend/init_db.py

# Test health
curl http://localhost:8000/api/health/ping
# Expected: {"status": "pong"}
```

**Total Time: ~5 minutes** ✅

---

## Access Application

| Service | URL | Default Login |
|---------|-----|---|
| **API** | http://localhost:8000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **Health** | http://localhost:8000/api/health/full | - |
| **MongoDB** | localhost:27017 | admin/changeme |
| **Prometheus** | http://localhost:9090 | - |
| **Grafana** | http://localhost:3000 | admin/admin |

---

## Useful Podman Commands

```bash
# View running containers
podman ps

# View all containers
podman ps -a

# View logs
podman-compose logs api
podman-compose logs -f mongodb

# Execute command in container
podman exec <container_id> bash

# Stop all services
podman-compose down

# Clean up (remove volumes)
podman-compose down -v
```

---

## Verify System

```bash
# Run verification
podman-compose exec api python system_check.py

# Expected: ✓ SYSTEM VERIFIED - All checks passed!
```

---

## Key Differences from Docker (Minimal!)

| Feature | Docker | Podman |
|---------|--------|--------|
| Build | `docker build` | `podman build` |
| Run | `docker run` | `podman run` |
| Compose | `docker-compose` | `podman-compose` |
| Commands | Most identical | ✅ All identical |

---

## Rootless Mode (Recommended)

```bash
# Run without sudo (Linux)
podman-compose up -d

# View rootless containers
podman ps

# Still need sudo? (shouldn't)
# Fix with: podman system migrate
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Can't pull images | Check network: `podman run busybox ping 8.8.8.8` |
| Port 8000 in use | Change PORT in .env or: `lsof -i :8000` |
| MongoDB won't connect | Check .env MONGODB_URI |
| High memory | Reduce workers in config |

---

## Production Readiness

After 5-minute setup, verify:

✅ `podman-compose ps` shows all 5 services running  
✅ `curl http://localhost:8000/api/health/full` returns healthy  
✅ `podman-compose exec api python system_check.py` all pass  
✅ Dashboards accessible (Grafana at :3000)  

**You're production-ready!** 🎉

---

## Next: Deploy to Production

See `PODMAN_DEPLOYMENT_GUIDE.md` for:
- ✅ Systemd integration
- ✅ Security hardening  
- ✅ Kubernetes deployment
- ✅ Scaling strategies
- ✅ Monitoring setup

---

**Time to Deploy:** 5 minutes  
**Docker Knowledge Required:** None - Podman commands are identical!  
**Status:** ✅ READY
