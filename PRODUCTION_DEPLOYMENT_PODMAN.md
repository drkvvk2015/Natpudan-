# Natpudan AI Medical Assistant - Podman Production Deployment

## 🚀 Quick Start

```powershell
# 1. Prepare environment
.\.venv\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt

# 2. Configure production environment
cp .env.prod .env.prod.local
# Edit .env.prod.local with your secrets

# 3. Deploy with Podman
.\deploy-podman-production.ps1 -EnvFile .env.prod.local -Recreate -Pull
```

---

## 📋 Pre-Deployment Checklist

### 1. **Secrets Management**
- [ ] Generate 256-char random `SECRET_KEY` for JWT
- [ ] Obtain valid `OPENAI_API_KEY` from https://platform.openai.com
- [ ] Create strong PostgreSQL password (20+ chars, mixed case, numbers, symbols)
- [ ] Generate Redis password for secure deployment

### 2. **Domain & SSL/TLS**
- [ ] Register domain (e.g., api.yourdomain.com)
- [ ] Obtain SSL certificates:
  - **Option A**: Let's Encrypt (free) - Use Certbot
  - **Option B**: AWS Certificate Manager (if using AWS)
  - **Option C**: DigiCert/Comodo (paid)

### 3. **Infrastructure Requirements**
- [ ] Podman installed & running on production server
- [ ] podman-compose installed
- [ ] Minimum: 4GB RAM, 20GB disk, 2 CPU cores
- [ ] Recommended: 8GB RAM, 50GB disk, 4 CPU cores
- [ ] Open ports: 80 (HTTP), 443 (HTTPS), 5432 (PostgreSQL), 6379 (Redis)

### 4. **Monitoring & Logging**
- [ ] Set up log aggregation (ELK, Datadog, CloudWatch)
- [ ] Configure health monitoring (Prometheus, Grafana)
- [ ] Enable APScheduler for background tasks
- [ ] Set up email alerts for critical errors

---

## 🔧 Configuration Files

### 1. Update `.env.prod.local` with Production Values

```bash
# Critical: Change these before deploying!
SECRET_KEY=<256-char-random-string>
POSTGRES_PASSWORD=<strong-password>
OPENAI_API_KEY=sk-proj-<your-key>

# Domain configuration
FRONTEND_URL=https://api.yourdomain.com
VITE_API_BASE_URL=https://api.yourdomain.com
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Security
DEBUG=false
LOG_LEVEL=WARNING

# Optional: Error tracking
SENTRY_DSN=https://xxx@yyy.ingest.sentry.io/zzz
SENTRY_ENVIRONMENT=production

# APScheduler (KB refresh, integrity checks)
APSCHEDULER_ENABLED=true
KB_REFRESH_HOUR=14  # 2 PM UTC
```

### 2. Update `docker-compose.yml` for Production

Key changes needed:
- [ ] Change `postgres:15-alpine` to `postgres:15` (more stable)
- [ ] Add environment variables for all services
- [ ] Enable persistent storage for databases
- [ ] Add resource limits (CPU/RAM)
- [ ] Configure health checks with realistic timeouts
- [ ] Add logging configuration
- [ ] Remove hardcoded ports (use env vars)

---

## 🔒 Security Hardening

### 1. **SSL/TLS with Nginx Reverse Proxy**

```yaml
# Add to docker-compose.yml
nginx:
  image: nginx:alpine
  container_name: physician-ai-nginx
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    - ./nginx/ssl:/etc/nginx/ssl:ro
    - ./frontend/dist:/usr/share/nginx/html:ro
  depends_on:
    - backend
    - frontend
  restart: unless-stopped
  networks:
    - physician-ai-network
```

### 2. **Network Security**
- [ ] Run Podman on isolated network (done by default)
- [ ] Disable public access to PostgreSQL/Redis ports
- [ ] Use firewall rules to allow only needed ports
- [ ] Enable SELinux/AppArmor container restrictions

### 3. **Database Security**
```sql
-- After PostgreSQL starts, run:
REVOKE PUBLIC ON SCHEMA public FROM public;
GRANT USAGE ON SCHEMA public TO physician_user;
GRANT CREATE ON SCHEMA public TO physician_user;

-- Enable SSL for PostgreSQL connections
ALTER SYSTEM SET ssl = on;
```

### 4. **Application Security**
- [ ] Set `SECURE_COOKIES=true` in production
- [ ] Enable HSTS headers (12 months)
- [ ] Implement rate limiting (1000 req/hour)
- [ ] Enable CORS only for your domain
- [ ] Disable APScheduler `.start()` in async context (already done)

---

## 📊 Deployment Architecture

```
┌─────────────────────────────────────────┐
│         Production Server               │
├─────────────────────────────────────────┤
│                                         │
│  ┌────────────────────────────────┐    │
│  │    Nginx (SSL/TLS Termination) │    │
│  └────────────┬───────────────────┘    │
│               │                         │
│   ┌───────────┴────────────┬────────┐  │
│   │                        │        │  │
│ ┌─▼──────┐  ┌──────────┐ ┌▼──┐  ┌─▼──┐
│ │Backend │  │ Frontend │ │DB │  │Redis
│ │ Flask/ │  │  React   │ │PG │  │    │
│ │FastAPI │  │  Build   │ │15 │  │    │
│ └────────┘  └──────────┘ └───┘  └────┘
│   :8000        :3000      :5432  :6379
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   Celery Worker (Background)    │   │
│  │   - PDF processing              │   │
│  │   - KB refresh                  │   │
│  │   - Self-healing maintenance    │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
         ↓ External (HTTPS)
      https://yourdomain.com
```

---

## 🚢 Deployment Steps

### Phase 1: Local Testing (in Podman)

```powershell
# Activate environment
.\.venv\Scripts\Activate.ps1

# Build images
podman-compose -f docker-compose.yml build

# Test with staging configuration
podman-compose -f docker-compose.yml up -d

# Check service health
podman-compose -f docker-compose.yml ps
podman logs physician-ai-backend
podman logs physician-ai-frontend

# Run health checks
Invoke-WebRequest http://localhost:8000/health
Invoke-WebRequest http://localhost:3000/

# Cleanup
podman-compose -f docker-compose.yml down
```

### Phase 2: Production Deployment

```powershell
# 1. SSH into production server
ssh user@your-production-server

# 2. Clone/update repository
cd /opt/natpudan
git pull origin main

# 3. Copy production environment
cp .env.prod.local .env

# 4. Pull latest images
podman-compose pull

# 5. Start services with volumes
podman-compose -f docker-compose.yml up -d

# 6. Monitor startup (2-5 minutes)
podman-compose logs -f backend

# 7. Verify all services healthy
podman-compose ps
# All should show "running" with health "healthy"

# 8. Run smoke tests
curl https://yourdomain.com/health
curl https://yourdomain.com/api/health
```

### Phase 3: Post-Deployment Validation

```powershell
# Check services are responding
$services = @("backend", "frontend", "db", "redis")
foreach ($service in $services) {
    podman inspect physician-ai-$service
}

# Verify database connectivity
podman exec physician-ai-backend python -c "from app.database import init_db; init_db()"

# Check logs for errors
podman logs physician-ai-backend | Select-String -Pattern "ERROR|CRITICAL" -Context 2
podman logs physician-ai-frontend | Select-String -Pattern "ERROR"

# Test knowledge base loading
Invoke-WebRequest https://yourdomain.com/api/medical/knowledge/statistics -UseBasicParsing
```

---

## 📈 Performance Optimization

### 1. **Database Tuning** (PostgreSQL)
```sql
-- Run these in production PostgreSQL:
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET work_mem = '16MB';
ALTER SYSTEM SET wal_level = 'replica';
SELECT pg_reload_conf();
```

### 2. **Backend Optimization**
```python
# app/main.py settings for production:
- WORKERS=4 (instead of 1)
- WORKER_CLASS=uvicorn.workers.UvicornWorker
- TIMEOUT=120 (seconds)
- KEEPALIVE=5 (seconds)
```

### 3. **Redis Optimization**
```bash
# In docker-compose.yml Redis service:
command: >
  redis-server 
  --maxmemory 256mb 
  --maxmemory-policy allkeys-lru
  --appendonly yes
  --appendfsync everysec
```

### 4. **Frontend Build Optimization**
```bash
# In Dockerfile.frontend:
# Use multi-stage build to minimize image size
# Stage 1: Build (with node_modules)
# Stage 2: Production (only dist + nginx)
# Result: 5MB instead of 500MB
```

---

## 🔍 Monitoring & Maintenance

### 1. **Health Checks** (Every 5 minutes)

```powershell
function Monitor-Services {
    $backends = @(
        @{Name="Backend"; Url="http://localhost:8000/health"; Port=8000},
        @{Name="Frontend"; Url="http://localhost:3000/"; Port=3000},
        @{Name="Database"; Url=""; Port=5432}
    )
    
    foreach ($service in $backends) {
        try {
            if ($service.Url) {
                $response = Invoke-WebRequest -Uri $service.Url -UseBasicParsing -TimeoutSec 5
                Write-Host "✅ $($service.Name): Healthy" -ForegroundColor Green
            } else {
                Test-NetConnection -ComputerName localhost -Port $service.Port -InformationLevel Quiet
                Write-Host "✅ $($service.Name): Connected" -ForegroundColor Green
            }
        } catch {
            Write-Host "❌ $($service.Name): DOWN" -ForegroundColor Red
            # Alert: Send email/Slack notification
        }
    }
}
```

### 2. **Log Rotation** (Configure Docker logging)

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
    labels: "service=natpudan"
```

### 3. **Backup Strategy**

```powershell
# Daily backup script (run via cron)
$timestamp = Get-Date -Format "yyyy-MM-dd-HHmmss"
podman exec physician-ai-db pg_dump \
  -U physician_user -d physician_ai \
  -h localhost > "backup-$timestamp.sql"

# Upload to cloud storage (S3/Azure Blob)
aws s3 cp "backup-$timestamp.sql" s3://my-backups/
```

### 4. **APScheduler Configuration**

```python
# app/main.py - Enable scheduled tasks in production
scheduler = BackgroundScheduler()

# Daily: 2 PM UTC - Knowledge Base refresh
scheduler.add_job(kb_refresh, CronTrigger(hour=14, minute=0))

# Daily: 1 AM UTC - Index integrity check
scheduler.add_job(index_integrity_check, CronTrigger(hour=1, minute=0))

# Every 6 hours - Self-healing preventive maintenance
scheduler.add_job(preventive_maintenance, CronTrigger(hour='*/6'))

# Start in background thread (not blocking async)
from threading import Thread
Thread(daemon=True, target=scheduler.start).start()
```

---

## 🆘 Troubleshooting

### Backend won't start
```powershell
# Check logs
podman logs physician-ai-backend -n 50

# Verify database connectivity
podman exec physician-ai-backend \
  python -c "from sqlalchemy import create_engine; \
  engine = create_engine(os.getenv('DATABASE_URL')); \
  engine.connect()"

# Rebuild container
podman-compose down --volumes
podman-compose build --no-cache
podman-compose up -d
```

### High memory usage
```powershell
# Check memory stats
podman stats

# Adjust limits in docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 1G
    reservations:
      cpus: '1'
      memory: 512M
```

### Slow API responses
```powershell
# Enable query logging
DATABASE_ECHO=true  # in .env

# Check slow queries
podman exec physician-ai-db \
  psql -U physician_user -d physician_ai \
  -c "SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"

# Scale Celery workers
podman-compose scale celery=3
```

---

## 📝 Post-Deployment Checklist

- [ ] All services running and healthy
- [ ] Database initialized with admin user
- [ ] Knowledge base loading on first request
- [ ] Celery workers processing background tasks
- [ ] APScheduler running scheduled maintenance
- [ ] SSL/TLS certificates valid
- [ ] CORS configured for your domain only
- [ ] Rate limiting enabled
- [ ] Logging configured and monitored
- [ ] Backup jobs scheduled and tested
- [ ] Health check monitoring in place
- [ ] Error tracking (Sentry) configured
- [ ] Performance metrics being collected

---

## 🎯 What's Next?

1. **Kubernetes Deployment** (for high availability)
   - Use Helm charts for easier management
   - Auto-scaling based on load
   - Rolling updates without downtime

2. **CI/CD Pipeline** (GitHub Actions)
   - Automated tests on every commit
   - Build and push images to registry
   - Auto-deploy to production on main branch

3. **Multi-Region Replication** (DR/HA)
   - Replicate database across regions
   - Load balancing with GeoDNS
   - Disaster recovery testing

4. **Advanced Monitoring**
   - Custom Grafana dashboards
   - Prometheus metrics export
   - Real-time alerts for anomalies

---

## 📞 Support & Resources

- **Podman Docs**: https://docs.podman.io
- **Docker Compose Compatibility**: https://github.com/containers/podman-compose
- **PostgreSQL Production Tuning**: https://wiki.postgresql.org/wiki/Performance_Optimization
- **FastAPI Production Deployment**: https://fastapi.tiangolo.com/deployment/
- **Natpudan Health Endpoints**: `/health`, `/health/detailed`

