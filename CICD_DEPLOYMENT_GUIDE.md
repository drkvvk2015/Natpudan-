# CI/CD Deployment Guide

This guide explains how to deploy Natpudan AI using the automated CI/CD pipeline with pre-built Docker images.

## Overview

The CI/CD pipeline automatically builds and publishes Docker images to GitHub Container Registry (GHCR) whenever you push to the `main` or `develop` branches. These pre-built images can then be deployed to any server without needing to build locally.

## Architecture

```
GitHub Push → GitHub Actions → Build Images → Push to GHCR → Deploy Anywhere
```

## Setup Instructions

### 1. Enable GitHub Container Registry

1. Go to your GitHub repository settings
2. Navigate to **Settings** → **Actions** → **General**
3. Under "Workflow permissions", select **Read and write permissions**
4. Enable **Allow GitHub Actions to create and approve pull requests**

### 2. Configure Repository Secrets (Optional)

For additional security, you can add these secrets in **Settings** → **Secrets and variables** → **Actions**:

```
OPENAI_API_KEY         # Your OpenAI API key
SECRET_KEY             # JWT secret key
POSTGRES_PASSWORD      # Database password
```

### 3. Push Code to Trigger Build

```bash
git add .
git commit -m "Deploy application"
git push origin main
```

The GitHub Actions workflow will automatically:
- Build backend and frontend images
- Run tests (if configured)
- Push images to GHCR with tags:
  - `latest` (for main branch)
  - `branch-name` (for feature branches)
  - `v1.0.0` (for version tags)
  - `main-abc1234` (git commit SHA)

### 4. View Build Status

1. Go to the **Actions** tab in your GitHub repository
2. Click on the latest workflow run
3. Monitor the build progress for backend and frontend

### 5. Deploy to Production Server

Once images are built, deploy to any server:

#### Option A: Using Docker Compose (Recommended)

```bash
# On your production server

# 1. Clone the repository (or just copy docker-compose.production.yml)
git clone https://github.com/your-username/natpudan.git
cd natpudan

# 2. Copy and configure environment variables
cp .env.production.example .env.production
nano .env.production  # Edit with your values

# 3. Log in to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# 4. Pull and start services
export GITHUB_REPOSITORY_OWNER=your-username
export IMAGE_TAG=latest
docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml up -d

# 5. Check status
docker-compose -f docker-compose.production.yml ps
```

#### Option B: Using Kubernetes

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/services.yaml
```

#### Option C: Using Podman

```bash
# Pull images
podman pull ghcr.io/your-username/natpudan-backend:latest
podman pull ghcr.io/your-username/natpudan-frontend:latest

# Run with podman-compose
podman-compose -f docker-compose.production.yml up -d
```

## Image Tags

The CI/CD pipeline creates multiple tags for flexibility:

| Tag | Description | Example |
|-----|-------------|---------|
| `latest` | Latest stable build from main branch | `ghcr.io/user/natpudan-backend:latest` |
| `develop` | Latest development build | `ghcr.io/user/natpudan-backend:develop` |
| `v1.0.0` | Semantic version tag | `ghcr.io/user/natpudan-backend:v1.0.0` |
| `main-abc1234` | Commit SHA tag | `ghcr.io/user/natpudan-backend:main-abc1234` |

## Deployment Scenarios

### Scenario 1: Fresh Production Deployment

```bash
# 1. Set up environment
export GITHUB_REPOSITORY_OWNER=your-username
export IMAGE_TAG=latest
export OPENAI_API_KEY=sk-...
export SECRET_KEY=$(openssl rand -hex 32)
export POSTGRES_PASSWORD=$(openssl rand -base64 32)

# 2. Deploy
docker-compose -f docker-compose.production.yml up -d

# 3. Initialize database (first time only)
docker-compose -f docker-compose.production.yml exec backend python -m app.init_db

# 4. Create admin user
docker-compose -f docker-compose.production.yml exec backend python create_admin_user.py
```

### Scenario 2: Update Existing Deployment

```bash
# 1. Pull latest images
docker-compose -f docker-compose.production.yml pull

# 2. Restart services with new images
docker-compose -f docker-compose.production.yml up -d

# 3. Verify deployment
docker-compose -f docker-compose.production.yml ps
curl http://localhost:8000/health
```

### Scenario 3: Rollback to Previous Version

```bash
# 1. Find previous version tag (git commit SHA or version number)
docker images | grep natpudan-backend

# 2. Set IMAGE_TAG to previous version
export IMAGE_TAG=v1.0.0  # or main-abc1234

# 3. Deploy previous version
docker-compose -f docker-compose.production.yml up -d
```

### Scenario 4: Deploy to Multiple Environments

```bash
# Development
IMAGE_TAG=develop docker-compose -f docker-compose.production.yml up -d

# Staging
IMAGE_TAG=v1.1.0-rc1 docker-compose -f docker-compose.production.yml -p staging up -d

# Production
IMAGE_TAG=latest docker-compose -f docker-compose.production.yml -p production up -d
```

## Manual Workflow Trigger

You can manually trigger the build workflow:

1. Go to **Actions** tab
2. Select **Build and Push Docker Images** workflow
3. Click **Run workflow**
4. Choose branch and whether to push images
5. Click **Run workflow**

## Monitoring

### View Container Logs

```bash
# All services
docker-compose -f docker-compose.production.yml logs -f

# Specific service
docker-compose -f docker-compose.production.yml logs -f backend
docker-compose -f docker-compose.production.yml logs -f frontend

# Last 100 lines
docker-compose -f docker-compose.production.yml logs --tail=100 backend
```

### Check Health

```bash
# Backend health
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# Celery monitoring (Flower)
open http://localhost:5555
```

### Resource Usage

```bash
# Docker stats
docker stats

# Container details
docker-compose -f docker-compose.production.yml ps
docker-compose -f docker-compose.production.yml top
```

## Troubleshooting

### Build Fails in GitHub Actions

1. Check **Actions** tab for error logs
2. Verify Dockerfile syntax
3. Ensure all dependencies are in requirements.txt/package.json
4. Check if GitHub Actions has write permissions

### Cannot Pull Images

```bash
# Log in to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Make repository public or grant access
# Go to Settings → Packages → Package visibility
```

### Container Fails to Start

```bash
# Check logs
docker-compose -f docker-compose.production.yml logs backend

# Common issues:
# - Missing environment variables (check .env.production)
# - Database not ready (wait for health check)
# - Port already in use (change BACKEND_PORT/FRONTEND_PORT)
```

### Database Connection Errors

```bash
# Verify database is running
docker-compose -f docker-compose.production.yml ps db

# Check database logs
docker-compose -f docker-compose.production.yml logs db

# Test connection
docker-compose -f docker-compose.production.yml exec db psql -U physician_user -d physician_ai
```

## Best Practices

### Version Tagging

```bash
# Create a release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# GitHub Actions will automatically build and tag the image as v1.0.0
```

### Security

1. **Never commit secrets** to the repository
2. Use GitHub Secrets for sensitive data
3. Rotate secrets regularly
4. Use strong passwords for database and admin accounts
5. Enable SSL/TLS in production (configure nginx)

### Performance

1. Use specific version tags instead of `latest` in production
2. Configure resource limits in docker-compose.production.yml
3. Monitor with Flower (Celery) and health endpoints
4. Set up log rotation for container logs

### Backup

```bash
# Backup database
docker-compose -f docker-compose.production.yml exec db pg_dump -U physician_user physician_ai > backup.sql

# Backup volumes
docker run --rm -v natpudan_postgres-data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz /data
```

## Local Development vs Production

| Aspect | Local Development | Production Deployment |
|--------|------------------|----------------------|
| **Build** | Local `docker build` or `npm run dev` | GitHub Actions builds images |
| **Images** | Built on-demand, not pushed | Pre-built, pushed to GHCR |
| **Hot Reload** | Enabled (volume mounts) | Disabled (baked into image) |
| **Environment** | `.env` file | `.env.production` file |
| **Compose File** | `docker-compose.yml` | `docker-compose.production.yml` |
| **Database** | SQLite or PostgreSQL | PostgreSQL (persistent volume) |
| **SSL/TLS** | Not required | Nginx with SSL certificates |

## Continuous Deployment (Advanced)

For automatic deployment to servers after successful builds:

1. Add deployment secrets to GitHub:
   - `DEPLOY_HOST` - Production server IP
   - `DEPLOY_USER` - SSH user
   - `SSH_PRIVATE_KEY` - SSH key for authentication

2. Add deployment step to workflow:

```yaml
- name: Deploy to Production
  if: github.ref == 'refs/heads/main'
  uses: appleboy/ssh-action@master
  with:
    host: ${{ secrets.DEPLOY_HOST }}
    username: ${{ secrets.DEPLOY_USER }}
    key: ${{ secrets.SSH_PRIVATE_KEY }}
    script: |
      cd /opt/natpudan
      docker-compose -f docker-compose.production.yml pull
      docker-compose -f docker-compose.production.yml up -d
```

## Support

For issues or questions:
- Check GitHub Actions logs
- Review container logs: `docker-compose logs`
- Open an issue in the repository
- Check documentation in `README.md` and `QUICKSTART_GUIDE.md`
