# 🎯 EduPath Optimizer - Podman Deployment Guide

## What is Podman?

Podman is a daemonless container engine that's **drop-in compatible with Docker**. Key advantages:

✅ No daemon required (more secure)  
✅ Rootless container support  
✅ Pod management built-in  
✅ Drop-in Docker replacement (just replace `docker` with `podman`)  
✅ Better resource isolation  
✅ Kubernetes-native pod support  

---

## Installation

### Windows 10/11 with WSL2

```bash
# Install Podman Desktop (GUI)
# From: https://podman.io/docs/installation#windows

# Or via Chocolatey
choco install podman

# After installation, initialize
podman machine init
podman machine start
```

### Linux (Ubuntu/Debian)

```bash
# Install Podman
sudo apt-get update
sudo apt-get install -y podman podman-compose

# Start and enable
sudo systemctl start podman
sudo systemctl enable podman
```

### macOS

```bash
# Via Homebrew
brew install podman

# Initialize machine
podman machine init
podman machine start
```

---

## Quick Start with Podman

### Step 1: Verify Installation

```bash
# Check Podman version
podman --version

# Expected: podman version X.X.X

# Test basic functionality
podman run hello-world

# Expected: Hello from Podman!
```

### Step 2: Prepare Configuration

```bash
cd /e/SGP/EduPath_Optimizer

# Create production .env
cp .env.example .env

# Edit with your values
nano .env
```

### Step 3: Build Image

```bash
# Build the image
podman build -t edupath-optimizer:latest .

# Verify image created
podman images | grep edupath-optimizer
```

### Step 4: Run with Podman Compose

```bash
# Install podman-compose if needed
pip install podman-compose

# Start all services
podman-compose up -d

# Or use Podman pods directly (see below)
```

### Step 5: Verify Deployment

```bash
# Check running containers
podman ps

# Check health
podman exec $(podman ps -q -f "label=service=api") curl http://localhost:8000/api/health/ping

# View logs
podman logs -f <container_id>
```

---

## Rootless Container Setup (Recommended for Security)

### Setup Rootless Mode

```bash
# Install requisites
sudo apt-get install -y slirp4netns fuse-overlayfs

# Configure current user
podman system migrate

# Verify rootless mode
podman unshare whoami
# Expected: root (inside the namespace)
```

### Run in Rootless Mode

```bash
# Start services without sudo
podman-compose up -d

# Check services
podman ps

# Access from host
curl http://localhost:8000/api/health/ping
```

---

## Podman Pod Management (Native Approach)

### Alternative: Using Podman Pods

Instead of `podman-compose`, you can use native Podman pods:

```bash
# Create a pod
podman pod create --name edupath-app \
  -p 8000:8000 \
  -p 27017:27017 \
  -p 9090:9090 \
  -p 3000:3000

# Run API container in pod
podman run -d \
  --pod edupath-app \
  --name edupath-api \
  -e MONGODB_URI="mongodb://localhost:27017" \
  edupath-optimizer:latest

# Run MongoDB in same pod
podman run -d \
  --pod edupath-app \
  --name edupath-mongodb \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  mongo:7.0

# View pod status
podman pod ps
podman pod inspect edupath-app
```

---

## Common Podman Commands

### Container Management

```bash
# Build image
podman build -t edupath-optimizer:latest .

# Run container
podman run -d \
  --name edupath-api \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  edupath-optimizer:latest

# List containers
podman ps          # Running
podman ps -a       # All

# View logs
podman logs <container_id>
podman logs -f <container_id>  # Follow

# Stop/Start container
podman stop <container_id>
podman start <container_id>

# Remove container
podman rm <container_id>
```

### Image Management

```bash
# List images
podman images

# Remove image
podman rmi <image_id>

# Push to registry
podman push edupath-optimizer:latest docker.io/yourname/edupath-optimizer

# Pull image
podman pull docker.io/yourname/edupath-optimizer
```

### Debugging

```bash
# Execute command in running container
podman exec -it <container_id> bash

# Inspect container details
podman inspect <container_id>

# Check resource usage
podman stats

# View network
podman network ls
podman network inspect <network_name>
```

---

## Docker to Podman Migration

### Direct Replacement

For most cases, just replace `docker` with `podman`:

```bash
# Before (Docker)
docker build -t app:latest .
docker-compose up -d
docker ps

# After (Podman)
podman build -t app:latest .
podman-compose up -d
podman ps
```

### Using Podman with Docker Compose Files

```bash
# Use existing docker-compose.yml with Podman
podman-compose -f docker-compose.yml up -d

# Compose configuration is fully compatible
```

### Docker CLI Alias (Optional)

```bash
# Add Docker alias for Podman (on Linux/macOS)
alias docker=podman

# Then use Docker commands with Podman
docker build -t app:latest .
docker ps
```

---

## Podman Compose Deployment

### Using podman-compose.yml

The `docker-compose.yml` works directly with Podman Compose. No changes needed!

```bash
# Start all services
podman-compose up -d

# Expected output shows Podman pulling images and starting containers
# ✓ api service started
# ✓ mongodb service started
# ✓ nginx service started
# ✓ prometheus service started
# ✓ grafana service started
```

### View Services

```bash
# List all containers in compose stack
podman-compose ps

# Check specific service logs
podman-compose logs api
podman-compose logs -f mongodb

# Stop all services
podman-compose down

# Clean up volumes
podman-compose down -v
```

---

## Systemd Integration with Podman

### Create Systemd Service

```bash
# Generate systemd unit files
podman generate systemd --new --name edupath-api > /etc/systemd/system/edupath-api.service

# Reload and start
sudo systemctl daemon-reload
sudo systemctl enable edupath-api
sudo systemctl start edupath-api

# Check status
sudo systemctl status edupath-api
```

### Service File Example

```ini
[Unit]
Description=EduPath Optimizer Production Server
After=network.target

[Service]
Type=simple
User=edupath
WorkingDirectory=/opt/edupath
ExecStart=podman run \
  --rm \
  --name edupath-api \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  --env-file /opt/edupath/.env \
  edupath-optimizer:latest

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## Kubernetes Deployment (Podman-Native)

### Export to Kubernetes YAML

```bash
# Generate Kubernetes deployment from Podman
podman-compose -f docker-compose.yml config > kubernetes.yml

# Deploy to Kubernetes
kubectl apply -f kubernetes.yml
```

### Pod Distribution

```bash
# Distribute Podman pods to multiple machines
podman pod create --name edupath-app

# Export pod configuration
podman generate kube edupath-app > edupath-app.yaml

# Deploy on another machine
podman play kube edupath-app.yaml
```

---

## Networking with Podman

### Default Bridge Network

```bash
# Containers auto-connect
podman run -d \
  --network bridge \
  --name edupath-mongodb \
  mongo:7.0

podman run -d \
  --network bridge \
  --name edupath-api \
  -p 8000:8000 \
  edupath-optimizer:latest
```

### Custom Network

```bash
# Create custom network
podman network create edupath-network

# Connect containers to network
podman run -d \
  --network edupath-network \
  --name edupath-mongodb \
  mongo:7.0

podman run -d \
  --network edupath-network \
  --name edupath-api \
  -p 8000:8000 \
  edupath-optimizer:latest

# Containers can communicate by name
podman exec edupath-api ping edupath-mongodb
```

---

## Volume Management

### Named Volumes

```bash
# Create named volume
podman volume create mongodb_data

# Inspect volume
podman volume inspect mongodb_data

# Use in container
podman run -d \
  -v mongodb_data:/data/db \
  mongo:7.0

# List volumes
podman volume ls

# Remove volume
podman volume rm mongodb_data
```

### Bind Mounts

```bash
# Mount host directory into container
podman run -d \
  -v /host/path:/container/path \
  mongo:7.0

# Read-only mount
podman run -d \
  -v /host/path:/container/path:ro \
  mongo:7.0
```

---

## Health Checks with Podman

### Container Health Status

```bash
# Run container with health check
podman run -d \
  --health-cmd='curl -f http://localhost:8000/api/health/ping || exit 1' \
  --health-interval=30s \
  --health-timeout=10s \
  --health-start-period=40s \
  --health-retries=3 \
  -p 8000:8000 \
  edupath-optimizer:latest

# Check health status
podman ps

# View health details
podman inspect --format='{{json .State.Health}}' <container_id> | jq
```

---

## Resource Limits with Podman

### CPU and Memory Limits

```bash
# Limit CPU (0.5 = half core)
podman run -d \
  --cpus=0.5 \
  edupath-optimizer:latest

# Limit memory (512MB)
podman run -d \
  -m 512m \
  edupath-optimizer:latest

# Combined limits
podman run -d \
  --cpus=1 \
  -m 2G \
  --name edupath-api \
  -p 8000:8000 \
  edupath-optimizer:latest
```

---

## Security with Podman

### Rootless Containers (Recommended)

```bash
# Run without root
podman run --userns=keep-id \
  -v /var/run/user/1000:/var/run/user/1000 \
  edupath-optimizer:latest
```

### Read-Only Root Filesystem

```bash
# Container can't modify root
podman run -d \
  --read-only \
  -v /tmp \
  -v /var/tmp \
  edupath-optimizer:latest
```

### Security Options

```bash
# Drop dangerous capabilities
podman run -d \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \
  -p 8000:8000 \
  edupath-optimizer:latest
```

---

## Troubleshooting Podman

### Issue: Cannot pull images

**Solution:**
```bash
# Check if Podman is running
podman info

# For rootless, ensure user namespace setup
podman unshare whoami

# Check network connectivity
podman run busybox ping 8.8.8.8
```

### Issue: Port already in use

**Solution:**
```bash
# Find container using port
podman ps -a | grep 8000

# Stop the container
podman stop <container_id>

# Or use different port
podman run -p 8001:8000 edupath-optimizer:latest
```

### Issue: Volumes not accessible

**Solution:**
```bash
# Check volume permissions
podman volume inspect <volume_name>

# Fix permissions
sudo chown -R 1000:1000 /var/lib/containers/storage/volumes/<volume>
```

### Issue: Networking between containers not working

**Solution:**
```bash
# Use custom network
podman network create mynet
podman run --network mynet --name app app:latest
podman run --network mynet --name db mongo:latest

# Test connectivity
podman exec app ping db
```

---

## Monitoring Podman

### Podman Stats

```bash
# View live resource usage
podman stats

# Single container
podman stats <container_id>

# Refresh interval
podman stats --interval 5
```

### Container Events

```bash
# Monitor all events
podman events

# Filter by container
podman events --filter container=edupath-api

# JSON format
podman events --format json
```

---

## Production Checklist for Podman

- [ ] Podman installed and verified
- [ ] Images built successfully
- [ ] Containers run in rootless mode
- [ ] Health checks configured
- [ ] Resource limits set
- [ ] Volumes initialized and mounted
- [ ] Networks configured properly
- [ ] Systemd services created
- [ ] Backup procedures tested
- [ ] Monitoring configured

---

## Podman Deployment Command

### Complete Production Setup

```bash
# 1. Build image
podman build -t edupath-optimizer:latest .

# 2. Start with compose
podman-compose up -d

# 3. Initialize database
podman-compose exec api python backend/init_db.py

# 4. Verify health
podman-compose exec api python system_check.py

# 5. View status
podman-compose ps
```

---

## Advantages of Podman Over Docker

| Feature | Docker | Podman |
|---------|--------|--------|
| **Daemon** | ✅ Required | ❌ Not needed |
| **Security** | Builtin | ✅ Better (rootless) |
| **CLI** | Docker CLI | ✅ Same/Compatible |
| **Compose** | docker-compose | ✅ podman-compose |
| **Pods** | No | ✅ Yes (K8s native) |
| **Resource Usage** | Higher | ✅ Lower |

---

## Migration Summary

### From Docker to Podman

```bash
# Before (Docker)
docker build -t app .
docker-compose up -d
docker ps
docker logs app

# After (Podman) - Identical commands!
podman build -t app .
podman-compose up -d
podman ps
podman logs app
```

**Drop-in replacement - minimal changes needed!**

---

## Next Steps

1. ✅ Install Podman
2. ✅ Build image: `podman build -t edupath-optimizer:latest .`
3. ✅ Start services: `podman-compose up -d`
4. ✅ Initialize DB: `podman-compose exec api python backend/init_db.py`
5. ✅ Verify: `podman-compose ps`

---

**Status:** ✅ Ready for Podman Deployment  
**Compatibility:** 100% with existing docker-compose.yml  
**Security:** ✅ Rootless mode recommended  
**Performance:** ✅ Better resource usage than Docker
