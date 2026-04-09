# 🔄 Docker to Podman Migration Guide

## About Podman

Podman is a **daemonless alternative to Docker** with better security and lower resource usage. The best part? It's **almost 100% compatible** - your `docker-compose.yml` works as-is!

---

## Why Migrate to Podman?

| Benefit | Docker | Podman |
|---------|--------|--------|
| **Daemon Required** | ✅ Yes | ❌ No |
| **Security** | Good | ✅ Better (rootless) |
| **Resource Usage** | Higher | ✅ Lower |
| **Docker CLI Compatible** | N/A | ✅ Yes |
| **Pod Support** | No | ✅ Yes (K8s native) |
| **User Namespace** | Limited | ✅ Full support |

---

## Installation & Setup

### Linux (Ubuntu/Debian)

```bash
# Uninstall Docker (optional)
sudo apt-get remove docker.io docker-compose

# Install Podman
sudo apt-get update
sudo apt-get install -y podman podman-compose

# Verify
podman --version
podman-compose --version

# Test
podman run hello-world
```

### Windows (WSL2)

```bash
# Option 1: Podman Desktop (GUI)
# Download from https://podman.io/docs/installation#windows

# Option 2: Chocolatey
choco install podman

# Initialize and start
podman machine init
podman machine start

# Verify
podman --version
```

### macOS

```bash
# Homebrew
brew install podman podman-compose

# Initialize
podman machine init
podman machine start

# Verify
podman --version
```

---

## Migration Steps

### Step 1: Backup Current Setup (Optional)

```bash
# List current containers
podman ps -a

# Export images
podman save -o backup.tar <image_name>

# Backup volumes
ls -la /var/lib/containers/storage/volumes/
```

### Step 2: Direct Replacement

Just replace commands:

```bash
# Before (Docker)
docker build -t app:latest .
docker run -d -p 8000:8000 app:latest
docker-compose up -d

# After (Podman) - No changes needed!
podman build -t app:latest .
podman run -d -p 8000:8000 app:latest
podman-compose up -d
```

### Step 3: Update Scripts (If Any)

```bash
# Find all Docker references
grep -r "docker" . --include="*.sh"

# Replace in scripts
sed -i 's/docker/podman/g' your-script.sh
```

### Step 4: Update CI/CD (If Using)

**GitHub Actions:**
```yaml
# Update containers to use Podman
- name: Build with Podman
  run: |
    podman build -t app:latest .
    podman run -d -p 8000:8000 app:latest
```

**GitLab CI:**
```yaml
build:
  image: podman:latest
  script:
    - podman build -t app:latest .
    - podman push app:latest
```

---

## Compatibility Comparison

### 100% Compatible (No Changes Needed)

```bash
# ✅ These work exactly the same in Podman

podman build -t app:latest .
podman run -d -p 8000:8000 app:latest
podman-compose up -d
podman ps
podman logs container_id
podman stop container_id
podman rm container_id
podman exec container_id bash
podman network create mynet
podman volume create mydata
```

### Minor Differences (If Any)

```bash
# Docker
docker daemon  # No equivalent in Podman (not needed!)

# Podman uses machines for Mac/Windows
podman machine start
podman machine stop

# Docker Desktop GUI
# Podman Desktop (available at podman.io)
```

---

## Rootless Mode (Key Advantage)

### Setup Rootless (Linux)

```bash
# Most modern Linux allows rootless by default
# If not, configure:

sudo apt-get install slirp4netns fuse-overlayfs

# Migrate user namespace
podman system migrate

# Verify
podman unshare whoami
# Expected: root (in namespace, not actual root)
```

### Run Rootless (No sudo needed!)

```bash
# Before (Docker - needs sudo)
sudo docker build -t app .
sudo docker run -d app

# After (Podman - no sudo!)
podman build -t app .
podman run -d app
```

---

## docker-compose.yml → podman-compose.yml

Your existing `docker-compose.yml` works directly with Podman Compose!

```bash
# No changes needed, just run:
podman-compose -f docker-compose.yml up -d

# Or rename for clarity:
cp docker-compose.yml podman-compose.yml
podman-compose up -d
```

### If You Need a Separate File

```yaml
# podman-compose.yml - Can be identical to docker-compose.yml
version: '3.8'

services:
  api:
    image: edupath-optimizer:latest
    # ... (identical to Docker config)
```

---

## Migrating Existing Containers

### Option 1: Clean Start (Recommended)

```bash
# Stop and remove old Docker containers
podman-compose down -v

# Remove old images (optional)
podman rmi edupath-optimizer:latest

# Rebuild with Podman
podman build -t edupath-optimizer:latest .

# Start fresh
podman-compose up -d
```

### Option 2: Keep Existing Data

```bash
# Export Docker volumes to Podman format
podman volume create mongodb_data

# Copy data if needed
# (depends on your specific setup)

# Start Podman services
podman-compose up -d
```

---

## Volume Migration

### Docker to Podman Volumes

```bash
# List Docker volumes
docker volume ls

# List Podman volumes
podman volume ls

# Migrate named volume
podman volume create mydata

# Copy data between volumes (if needed)
docker run --rm -v old_data:/from -v mydata:/to \
  busybox cp -r /from/* /to/
```

### Bind Mounts (No Migration Needed)

```bash
# These work identically in both
podman run -v /host/path:/container/path app
```

---

## Network Migration

### Port Mapping

```bash
# Same syntax in Podman
podman run -p 8000:8000 -p 27017:27017 app:latest
```

### Custom Networks

```bash
# Create with same commands
podman network create mynet

# Connect containers
podman run --network mynet --name app app:latest
podman run --network mynet --name db mongo:latest
```

---

## Systemd Service Migration

### Docker Service

```ini
# /etc/systemd/system/docker-app.service
[Service]
ExecStart=/usr/bin/docker run -d app:latest
```

### Podman Service

```ini
# /etc/systemd/system/podman-app.service
[Service]
ExecStart=/usr/bin/podman run -d app:latest
# Identical!
```

---

## Performance Comparison

### Resource Usage (Example)

```bash
# Docker (with daemon)
ps aux | grep docker
# Shows daemon process consuming memory

# Podman (daemonless)
podman stats
# Lower baseline memory usage
```

### Startup Time

```bash
# Measure Docker startup
time docker run hello-world

# Measure Podman startup  
time podman run hello-world
# Usually faster in Podman (no daemon)
```

---

## Troubleshooting Migration

| Issue | Solution |
|-------|----------|
| Images not found | Rebuild: `podman build -t app . ` |
| Port conflict | Find process: `lsof -i :8000` |
| Network issues | Recreate network: `podman network create` |
| Permission denied | Use rootless setup or `sudo podman` |
| Containers won't start | Check logs: `podman logs container_id` |

---

## Verification After Migration

```bash
# Check Podman is running
podman --version

# Verify services started
podman-compose ps

# Test health endpoint
curl http://localhost:8000/api/health/ping

# Check logs
podman-compose logs -f api

# Verify database
podman exec edupath_mongodb mongo --eval "db.adminCommand('ping')"

# Run system checks
podman-compose exec api python system_check.py
```

---

## Rollback to Docker (If Needed)

```bash
# Stop Podman services
podman-compose down -v

# Install Docker
sudo apt-get install docker.io docker-compose

# Start Docker services
docker-compose up -d

# Restore from backup if needed
docker load -i backup.tar
```

---

## Migration Checklist

- [ ] Podman installed and verified
- [ ] docker-compose.yml works with podman-compose
- [ ] All services start correctly
- [ ] Health checks passing
- [ ] Backups completed
- [ ] CI/CD updated (if applicable)
- [ ] Team trained on Podman commands
- [ ] Monitoring configured
- [ ] Documentation updated

---

## Common Migration Issues & Fixes

### Issue: podman-compose not found

```bash
# Install podman-compose
pip install podman-compose

# Or use apt
sudo apt-get install podman-compose

# Or download manually
curl -o /usr/local/bin/podman-compose \
  https://raw.githubusercontent.com/containers/podman-compose/main/podman_compose.py
chmod +x /usr/local/bin/podman-compose
```

### Issue: Containers won't connect

```bash
# Create custom network
podman network create edupath-net

# Use in compose
podman-compose -f docker-compose.yml -p edupath up -d
```

### Issue: Volume permissions error

```bash
# Check volume ownership
podman volume inspect mydata

# Fix permissions (if needed)
sudo chown -R 1000:1000 /var/lib/containers/storage/volumes/
```

---

## Performance Tuning for Podman

### Resource Limits

```bash
# CPU limit (0.5 cores)
podman run --cpus=0.5 app:latest

# Memory limit (1GB)
podman run -m 1G app:latest

# Combined
podman run --cpus=1 -m 2G app:latest
```

### Cgroup V2 (Better resource management)

```bash
# Check if enabled
cat /proc/cgroups

# If not, enable in /etc/default/grub
GRUB_CMDLINE_LINUX="systemd.unified_cgroup_hierarchy=1"

# Update GRUB
sudo update-grub
```

---

## Advanced: Kubernetes Migration

### Export to Kubernetes YAML

```bash
# Generate Kubernetes manifests from podman-compose
podman-compose config > k8s-manifest.yaml

# Deploy to Kubernetes
kubectl apply -f k8s-manifest.yaml
```

### Pod Distribution

```bash
# Create pod
podman pod create --name edupath-app

# Export pod
podman generate kube edupath-app > edupath-app.yaml

# Deploy on another machine
podman play kube edupath-app.yaml
```

---

## Timeline & Planning

### Week 1: Preparation
- [ ] Install Podman on test machine
- [ ] Test with small app
- [ ] Document current Docker setup
- [ ] Create backup

### Week 2-3: Migration
- [ ] Migrate main application
- [ ] Run verification tests
- [ ] Update CI/CD pipelines
- [ ] Train team

### Week 4: Production
- [ ] Migrate production environment
- [ ] Monitor for issues
- [ ] Optimize performance
- [ ] Full documentation

---

## Success Criteria

✅ All services running in Podman  
✅ All health checks passing  
✅ Database connected  
✅ Performance equal or better  
✅ Team comfortable with Podman  
✅ CI/CD updated  
✅ Backups verified  

---

## Need Help?

- Docker syntax: Works in Podman (just switch command name)
- Podman docs: https://podman.io/docs
- Podman GitHub: https://github.com/containers/podman
- Comparisons: https://podman.io/whatis.html

---

**Status:** ✅ Ready for Podman Migration  
**Effort:** ~1-2 hours for complete migration  
**Risk:** Low (roll back available)  
**Benefit:** Better security, lower resources
