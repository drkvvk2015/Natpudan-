# Docker Desktop Setup Guide for Natpudan AI

This guide helps you set up Docker Desktop as an alternative to Podman for better Windows compatibility.

## Why Docker Desktop?

- **Better Windows compatibility** - No process management issues
- **Stable docker-compose** - More reliable than podman-compose
- **GUI dashboard** - Easy to monitor containers
- **BuildKit support** - Faster builds with better caching

## Installation

### 1. Download Docker Desktop

Download from: https://www.docker.com/products/docker-desktop/

### 2. Install with WSL 2 Backend

1. Run the installer
2. Enable "Use WSL 2 instead of Hyper-V" (recommended)
3. Complete installation and restart computer

### 3. Configure Docker Desktop

1. Open Docker Desktop
2. Go to **Settings** → **Resources** → **Advanced**
3. Allocate resources:
   - **CPUs**: 4 or more
   - **Memory**: 8 GB or more
   - **Disk size**: 60 GB or more

4. Go to **Settings** → **Docker Engine**
5. Add to configuration:
```json
{
  "builder": {
    "gc": {
      "enabled": true,
      "defaultKeepStorage": "20GB"
    }
  },
  "features": {
    "buildkit": true
  }
}
```

6. Click **Apply & Restart**

## Using Docker Desktop with Natpudan

### Quick Start (Development)

```powershell
# Start local development (hybrid: local code + containers for databases)
.\start-dev.ps1

# Backend: http://localhost:8000
# Frontend: http://localhost:5173
```

### Full Container Deployment (Using Pre-built Images)

```powershell
# 1. Log in to GitHub Container Registry
$env:GITHUB_TOKEN = "your_github_token_here"
echo $env:GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# 2. Set environment variables
$env:GITHUB_REPOSITORY_OWNER = "YOUR_USERNAME"
$env:IMAGE_TAG = "latest"
$env:OPENAI_API_KEY = "sk-your-key"
$env:SECRET_KEY = "your-secret-key"

# 3. Deploy using production compose file
docker-compose -f docker-compose.production.yml up -d

# 4. Check status
docker-compose -f docker-compose.production.yml ps

# 5. View logs
docker-compose -f docker-compose.production.yml logs -f
```

### Local Build (If not using CI/CD)

```powershell
# Build all images locally
docker-compose build

# Start all services
docker-compose up -d

# Check health
docker ps
curl http://localhost:8000/health
curl http://localhost:3000
```

## Docker Desktop Dashboard

After starting containers, open Docker Desktop to:

1. **View running containers** - See status, logs, and resource usage
2. **Inspect containers** - Click on a container to see details
3. **View logs** - Real-time log streaming with search
4. **Open terminal** - Execute commands inside containers
5. **Manage volumes** - View and clean up volumes
6. **Manage images** - See all images and sizes

## Common Commands

```powershell
# View all containers
docker ps -a

# Stop all containers
docker-compose -f docker-compose.production.yml down

# Remove all containers and volumes (CAUTION: deletes data)
docker-compose -f docker-compose.production.yml down -v

# View logs for specific service
docker-compose -f docker-compose.production.yml logs -f backend

# Execute command in running container
docker-compose -f docker-compose.production.yml exec backend python -m app.init_db

# Rebuild single service
docker-compose -f docker-compose.production.yml up -d --build backend

# Scale service
docker-compose -f docker-compose.production.yml up -d --scale backend=3
```

## Troubleshooting

### Issue: Docker Desktop won't start

**Solution:**
1. Enable WSL 2: `wsl --install`
2. Update WSL: `wsl --update`
3. Restart computer

### Issue: Build is slow

**Solution:**
```powershell
# Enable BuildKit
$env:DOCKER_BUILDKIT = "1"
$env:COMPOSE_DOCKER_CLI_BUILD = "1"

# Use CI/CD pipeline instead for faster builds
```

### Issue: Out of disk space

**Solution:**
```powershell
# Clean up unused images
docker image prune -a

# Clean up volumes
docker volume prune

# Clean up everything (CAUTION)
docker system prune -a --volumes
```

### Issue: Containers can't connect

**Solution:**
1. Check if containers are on same network: `docker network ls`
2. Inspect network: `docker network inspect natpudan_default`
3. Recreate network: `docker-compose down` then `docker-compose up -d`

## Switching from Podman to Docker

If you were using Podman before:

```powershell
# 1. Stop all Podman containers
podman stop $(podman ps -aq)

# 2. Remove Podman containers (optional)
podman rm $(podman ps -aq)

# 3. Uninstall Podman (optional)
# Go to Windows Settings → Apps → Podman Desktop → Uninstall

# 4. Use Docker commands (same syntax as Podman)
docker ps
docker images
docker-compose up -d
```

## Performance Tips

1. **Use volume mounts for development:**
   ```yaml
   volumes:
     - ./backend:/app  # Hot reload enabled
   ```

2. **Use multi-stage builds:**
   ```dockerfile
   FROM node:20 AS build
   # Build stage
   FROM nginx:alpine
   # Production stage
   ```

3. **Cache dependencies:**
   ```dockerfile
   COPY package.json package-lock.json ./
   RUN npm install
   COPY . .
   ```

4. **Use .dockerignore:**
   ```
   node_modules
   .git
   .venv
   __pycache__
   ```

## Next Steps

1. **Enable Kubernetes** (optional):
   - Settings → Kubernetes → Enable Kubernetes
   - Deploy with kubectl: `kubectl apply -f k8s/`

2. **Set up CI/CD**:
   - Push code to GitHub
   - GitHub Actions builds images
   - Pull and deploy pre-built images

3. **Production deployment**:
   - Use docker-compose.production.yml
   - Set up SSL with nginx
   - Configure backups

## Resources

- Docker Desktop Docs: https://docs.docker.com/desktop/
- Docker Compose: https://docs.docker.com/compose/
- Dockerfile Best Practices: https://docs.docker.com/develop/dev-best-practices/
