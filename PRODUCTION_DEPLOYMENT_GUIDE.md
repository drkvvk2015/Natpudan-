# Natpudan AI - Production Deployment Guide (Docker)

## Overview
This guide covers deploying Natpudan to production using Docker Compose on a Linux server (AWS, DigitalOcean, Azure VM, etc.).

**Architecture:**
```
Nginx (Reverse Proxy, SSL/TLS) → Backend (4 workers) → PostgreSQL
                              → Frontend (React)
                              → Celery Worker (PDF processing, KB updates)
                              → Redis (Broker, Caching)
                              → Flower (Task Monitoring)
```

---

## Pre-Deployment Checklist

### 1. Environment Setup

Copy the production env file and customize it:

```bash
cd backend
cp .env.production .env
```

**Critical settings to update:**

| Variable | Action | Example |
|----------|--------|---------|
| `SECRET_KEY` | Generate random 32+ char string | Use: `openssl rand -hex 32` |
| `OPENAI_API_KEY` | Your OpenAI API key | `sk-proj-...` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@db:5432/natpudan_prod` |
| `CORS_ORIGINS` | Your frontend domain(s) | `https://app.yourdomain.com` |
| `CELERY_BROKER_URL` | Redis broker (auto in Docker) | `redis://redis:6379/0` |
| `REDIS_URL` | Redis cache (auto in Docker) | `redis://redis:6379/0` |

### 2. Security Hardening

- [ ] Change default Flower credentials:
  - Edit `docker-compose.yml`: `--basic_auth=admin:changeme` → `--basic_auth=admin:<strong-password>`
- [ ] Generate strong SECRET_KEY:
  ```bash
  openssl rand -hex 32
  ```
- [ ] Update database credentials in `docker-compose.yml`:
  - Change `POSTGRES_PASSWORD=secure_password` to a strong password
  - Update `DATABASE_URL` to match
- [ ] Setup SSL/TLS certificates (if using Nginx):
  - Place certificates in `./nginx/ssl/` directory
  - Update `nginx.conf` with your domain

### 3. Server Preparation

**Install Docker & Docker Compose on your server:**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y docker.io docker-compose git

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Allow your user to run Docker without sudo (optional)
sudo usermod -aG docker $USER
newgrp docker
```

**Clone your repository:**

```bash
cd /opt
git clone https://github.com/yourusername/Natpudan-.git
cd Natpudan-
git checkout clean-main2  # or your production branch
```

---

## Deployment Steps

### Step 1: Prepare Environment Variables

```bash
cd backend

# Copy production template
cp .env.production .env

# Edit with your production values
nano .env
```

**Minimum required values:**
```dotenv
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<your-generated-secret-key>
OPENAI_API_KEY=<your-openai-key>
DATABASE_URL=postgresql://physician_user:strong_password@db:5432/physician_ai
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Step 2: Update docker-compose.yml for Production

Update database credentials and secrets:

```bash
# Edit docker-compose.yml
nano docker-compose.yml
```

Replace:
- `POSTGRES_PASSWORD=secure_password` → use your strong password
- `--basic_auth=admin:changeme` → use your admin password
- Adjust replica/worker counts based on your server capacity

### Step 3: Build and Start Containers

```bash
# Build images (first time only, or after code changes)
docker-compose build

# Start all services in background
docker-compose up -d

# View logs
docker-compose logs -f

# Check service health
docker-compose ps
```

Expected output:
```
NAME                      STATUS
physician-ai-backend      Up (healthy)
physician-ai-frontend     Up
physician-ai-celery       Up
physician-ai-flower       Up
physician-ai-redis        Up (healthy)
physician-ai-db           Up (healthy)
physician-ai-nginx        Up
```

### Step 4: Initialize Database

```bash
# Run database migrations (if using Alembic)
docker-compose exec backend alembic upgrade head

# Or initialize schema directly
docker-compose exec backend python init_db_manual.py
```

### Step 5: Verify Deployment

```bash
# Test backend health
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000

# Check Flower (task monitoring)
# Open browser: http://your-server-ip:5555 (admin/your-password)

# Test a background task
docker-compose exec backend python -c "
from app.tasks import heartbeat
heartbeat.delay()
"
```

---

## Production Access Points

| Service | URL | Username | Password |
|---------|-----|----------|----------|
| Frontend | `https://yourdomain.com` | - | - |
| Backend API | `https://yourdomain.com/api` | - | - |
| API Docs | `https://yourdomain.com/api/docs` | - | - |
| Flower | `http://yourdomain:5555` | admin | (in docker-compose) |

---

## Monitoring & Maintenance

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery
docker-compose logs -f flower
```

### Monitor Resources

```bash
# CPU, Memory, Network
docker stats

# Or with container names
docker stats physician-ai-backend physician-ai-celery
```

### Restart Services

```bash
# Restart specific service
docker-compose restart celery

# Restart all
docker-compose restart

# Full rebuild and restart
docker-compose down
docker-compose up -d --build
```

### Backup Database

```bash
# Backup PostgreSQL
docker-compose exec db pg_dump -U physician_user physician_ai > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
docker exec -i physician-ai-db psql -U physician_user physician_ai < backup.sql
```

### Cleanup Old Resources

```bash
# Remove stopped containers, unused images/volumes
docker system prune -a --volumes

# Or be selective
docker image prune  # Remove unused images
docker volume prune # Remove unused volumes
```

---

## Scaling & Performance Tuning

### Increase Backend Workers

Edit `docker-compose.yml`:

```yaml
backend:
  command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "8"]
```

### Increase Celery Concurrency

Edit `docker-compose.yml`:

```yaml
celery:
  command: celery -A app.celery_config worker --loglevel=info --concurrency=8 -E
```

### Adjust Resource Limits

Edit `docker-compose.yml`:

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
      reservations:
        cpus: '1'
        memory: 1G
```

---

## Troubleshooting

### Backend not starting

```bash
docker-compose logs backend
```

Common issues:
- Missing OPENAI_API_KEY → add to .env
- Database connection failed → check DATABASE_URL
- Port conflict → change port mapping in docker-compose.yml

### Celery worker not processing tasks

```bash
# Check Celery logs
docker-compose logs celery

# Check Redis connection
docker-compose exec redis redis-cli ping

# Verify broker URL
docker-compose exec celery env | grep CELERY
```

### Flower not accessible

```bash
# Flower requires Redis broker (not SQLite)
# Verify Redis is running:
docker-compose logs redis

# Check Flower is connected to Redis:
docker-compose logs flower
```

### Out of memory

```bash
# Check resource usage
docker stats

# Reduce concurrency or increase server RAM
# Edit docker-compose.yml worker counts
```

---

## SSL/TLS with Nginx

If not using a reverse proxy already, configure Nginx with Let's Encrypt:

```bash
# Generate cert with Certbot (from host)
sudo certbot certonly --standalone -d yourdomain.com

# Copy to nginx/ssl/
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/

# Update nginx.conf to use SSL
docker-compose restart nginx
```

---

## Deployment Success Checklist

- [ ] All 7 containers are running (`docker-compose ps`)
- [ ] Backend health check passes (`curl /health`)
- [ ] Frontend loads in browser
- [ ] API docs accessible (`/api/docs`)
- [ ] Database initialized
- [ ] OpenAI API working (test diagnosis endpoint)
- [ ] Celery worker processing tasks (check Flower)
- [ ] PDF uploads working and fast (~2 seconds for 300-page PDFs)
- [ ] Knowledge base searchable
- [ ] Logs monitoring in place

---

## Next Steps

1. **Setup monitoring**: Use Prometheus + Grafana or DataDog
2. **Setup backups**: Automated daily PostgreSQL backups
3. **Setup logging**: Centralized logs with ELK or Datadog
4. **Setup CI/CD**: Auto-deploy on git push
5. **Performance**: Load test with Artillery or k6

---

## Support Commands Quick Reference

```bash
# Full restart
docker-compose down && docker-compose up -d

# View all logs
docker-compose logs -f --tail=100

# Health check all services
for svc in backend frontend celery flower redis db nginx; do
  echo "$svc:"; docker-compose exec $svc true 2>&1 | grep -E "Error|OK" || echo "OK"
done

# Database dump
docker-compose exec db pg_dump -U physician_user physician_ai | gzip > backup.sql.gz

# Test task submission
docker-compose exec backend python -c "from app.tasks import heartbeat; print(heartbeat.delay())"
```
