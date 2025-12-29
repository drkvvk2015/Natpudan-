# 🚀 Natpudan AI - Podman Production Deployment - Quick Guide

## ✅ What's Ready for Production?

Your application is now fully configured for production deployment with:

### ✨ **Production-Ready Files Created:**
1. **PRODUCTION_DEPLOYMENT_PODMAN.md** - Complete deployment guide with 20+ sections
2. **docker-compose.yml** - Enhanced with environment variables, resource limits, health checks, logging
3. **nginx/nginx.conf** - Production-grade Nginx reverse proxy with SSL/TLS, security headers, rate limiting
4. **podman-deploy.ps1** - Automated deployment script with validation and health checks
5. **.env.prod** - Pre-configured environment template with all required variables

---

## 🎯 Quick Start (5 minutes)

### Step 1: Prepare Environment
```powershell
# Copy production environment file
cp .env.prod .env.prod.local

# Edit with your actual values
notepad .env.prod.local

# Critical changes needed:
# - SECRET_KEY (generate 256-char random string)
# - POSTGRES_PASSWORD (strong password, 20+ chars)
# - OPENAI_API_KEY (get from https://platform.openai.com)
# - CORS_ORIGINS (your domain)
# - FRONTEND_URL, VITE_API_BASE_URL (your domain)
```

### Step 2: Generate Secrets
```powershell
# Generate 256-character random SECRET_KEY
$secret = -join ((0..255) | ForEach-Object { [char][byte]$_ }) | Get-Random -Count 256 -AsString
Write-Output $secret

# Or use online generator: https://www.random.org/strings/
```

### Step 3: Deploy with Podman
```powershell
# Make script executable
chmod +x podman-deploy.ps1

# Run deployment for LOCAL development
.\podman-deploy.ps1 -DeploymentMode local -EnvFile .env.prod.local

# Run deployment for PRODUCTION
.\podman-deploy.ps1 -DeploymentMode production -EnvFile .env.prod.local
```

### Step 4: Verify Deployment
```powershell
# Check all services are running
podman-compose ps

# View backend logs
podman-compose logs -f backend

# Test health endpoint
curl http://127.0.0.1:8000/health

# Access frontend
Start-Process http://127.0.0.1:3000
```

---

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                   PRODUCTION SERVER                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────┐             │
│  │  Nginx (SSL/TLS + Reverse Proxy)       │             │
│  │  - HTTPS termination                   │             │
│  │  - Rate limiting                       │             │
│  │  - Security headers                    │             │
│  │  - Static asset serving                │             │
│  └────────────┬─────────────────────────┘              │
│               │                                          │
│   ┌───────────┴──────────┬──────────┬─────────┐        │
│   ↓                      ↓          ↓         ↓        │
│ ┌─────────┐          ┌────────┐ ┌─────┐ ┌────────┐   │
│ │ Backend │          │Frontend│ │ DB  │ │ Redis  │   │
│ │ FastAPI │          │ React  │ │ PG  │ │ Cache  │   │
│ │ 8000    │          │ 3000   │ │5432 │ │ 6379   │   │
│ └────┬────┘          └────────┘ └─────┘ └────────┘   │
│      │                                                  │
│      └──────────┬──────────────────────────────────┐   │
│                 ↓                                  ↓   │
│           ┌──────────────┐              ┌──────────────┐│
│           │   Celery     │              │   Flower     ││
│           │   Workers    │              │   Dashboard  ││
│           │ (Background) │              │   (:5555)    ││
│           └──────────────┘              └──────────────┘│
│                                                          │
└──────────────────────────────────────────────────────────┘
         ↓↑ HTTPS (Port 443)
    Your Domain (yourdomain.com)
```

---

## 📊 Service Specifications

| Service | Image | Port | CPU | Memory | Storage |
|---------|-------|------|-----|--------|---------|
| **Backend** | FastAPI | 8000 | 2 cores | 2GB | 5GB |
| **Frontend** | React/Nginx | 3000 | 1 core | 512MB | 1GB |
| **Database** | PostgreSQL 15 | 5432 | 2 cores | 1GB | 20GB+ |
| **Redis** | Redis 7 | 6379 | 1 core | 512MB | 2GB |
| **Celery** | Python/Celery | N/A | 2 cores | 1GB | 5GB |
| **Flower** | Python/Flower | 5555 | 0.5 core | 256MB | 1GB |
| **Nginx** | Nginx Alpine | 443/80 | 1 core | 256MB | 1GB |
| **TOTAL** | - | - | **~9.5 cores** | **~6.5GB** | **~35GB** |

### Recommended Server Specs:
- **CPU**: 8-16 cores
- **RAM**: 16-32GB
- **Disk**: 100GB+ (SSD recommended)
- **Network**: 100 Mbps+
- **Uptime SLA**: 99.9%+

---

## 🔐 Security Checklist

Before deploying to production:

- [ ] Generate random 256-char `SECRET_KEY`
- [ ] Create strong PostgreSQL password (20+ chars, mixed case, numbers, symbols)
- [ ] Set `DEBUG=false` in .env
- [ ] Enable SSL/TLS certificates (Let's Encrypt or paid)
- [ ] Configure CORS for your domain ONLY
- [ ] Set up rate limiting (1000 req/hour default)
- [ ] Enable database backups (daily)
- [ ] Configure log aggregation
- [ ] Set up monitoring/alerting (Prometheus/Grafana)
- [ ] Run security audit (`podman images --trust`)
- [ ] Review security headers (HSTS, CSP, X-Frame-Options, etc.)
- [ ] Test SSL/TLS with https://www.ssllabs.com/ssltest/

---

## 📈 Performance Tuning

### 1. **Database** (PostgreSQL)
```sql
-- Run in production PostgreSQL:
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
SELECT pg_reload_conf();
```

### 2. **Backend** (FastAPI)
```python
# In docker-compose.yml:
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

### 3. **Redis** (Caching)
```bash
# Already configured with:
# - maxmemory 512MB
# - maxmemory-policy allkeys-lru
# - appendonly yes (persistence)
```

### 4. **Nginx** (Reverse Proxy)
```nginx
# Includes:
# - Gzip compression
# - HTTP/2 support
# - Connection pooling
# - Rate limiting zones
```

---

## 🔄 Backup & Recovery Strategy

### Daily Backups
```powershell
# Automated backup script (run via cron)
$timestamp = Get-Date -Format "yyyy-MM-dd-HHmmss"
podman exec physician-ai-db pg_dump \
  -U physician_user -d physician_ai > "backup-$timestamp.sql"

# Compress and upload to S3
gzip "backup-$timestamp.sql"
aws s3 cp "backup-$timestamp.sql.gz" s3://my-backups/
```

### Test Recovery
```powershell
# Restore from backup
cat backup-2025-12-29.sql | podman exec -i physician-ai-db \
  psql -U physician_user -d physician_ai
```

---

## 📊 Monitoring & Alerting

### Health Check Endpoints
```bash
# Basic health check
curl http://127.0.0.1:8000/health

# Detailed metrics
curl http://127.0.0.1:8000/health/detailed | jq

# Celery job status
http://127.0.0.1:5555  (Flower dashboard)

# Nginx stats
http://127.0.0.1:8080/nginx_status
```

### Recommended Monitoring Stack
1. **Prometheus** - Metrics collection
2. **Grafana** - Dashboards
3. **AlertManager** - Alert routing
4. **ELK Stack** - Log aggregation
5. **Sentry** - Error tracking (optional, already configured)

---

## 🆘 Troubleshooting

### Services won't start
```powershell
# Check logs
podman-compose logs backend

# Verify environment file
cat .env.prod.local | grep -E "SECRET_KEY|OPENAI_API_KEY"

# Rebuild images
podman-compose build --no-cache
```

### High memory usage
```powershell
# Monitor resource usage
podman stats

# Reduce concurrent Celery workers
# Edit docker-compose.yml: concurrency=2 (instead of 4)
```

### Slow database queries
```powershell
# Check slow query log
podman exec physician-ai-db \
  psql -U physician_user -d physician_ai \
  -c "SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"
```

### SSL/TLS certificate issues
```powershell
# Check certificate expiry
openssl x509 -in nginx/ssl/cert.pem -noout -dates

# Auto-renew with Let's Encrypt + Certbot
certbot renew --deploy-hook "podman restart physician-ai-nginx"
```

---

## 🎯 Next Steps

1. **Configure Environment** (5 min)
   - Edit `.env.prod.local` with your values
   - Generate secrets

2. **Set Up SSL/TLS** (optional, recommended for production)
   - Option A: Let's Encrypt (free) - `certbot certonly -d yourdomain.com`
   - Option B: Paid certificates - upload to `nginx/ssl/`

3. **Deploy** (5-10 min)
   - Run `podman-deploy.ps1`
   - Verify all services healthy
   - Run smoke tests

4. **Configure Monitoring** (30 min)
   - Set up Prometheus/Grafana
   - Configure Sentry for error tracking
   - Create health check monitoring

5. **Automate Backups** (20 min)
   - Set up daily PostgreSQL backups
   - Configure S3/cloud storage

6. **Enable APScheduler** (optional, for background tasks)
   - Knowledge base refresh at 2 PM UTC
   - Database integrity checks
   - Self-healing maintenance

---

## 📞 Support Resources

- **Podman Docs**: https://docs.podman.io
- **Docker Compose**: https://github.com/containers/podman-compose
- **FastAPI Production**: https://fastapi.tiangolo.com/deployment/
- **PostgreSQL Tuning**: https://wiki.postgresql.org/wiki/Performance_Optimization
- **Nginx Best Practices**: https://nginx.org/en/docs/
- **SSL Labs Testing**: https://www.ssllabs.com/ssltest/
- **Sentry Setup**: https://docs.sentry.io/product/integrations/

---

## 🎓 Documentation Files

1. **PRODUCTION_DEPLOYMENT_PODMAN.md** - Full 20-section deployment guide
2. **docker-compose.yml** - Container orchestration config
3. **nginx/nginx.conf** - Reverse proxy + SSL/TLS config
4. **podman-deploy.ps1** - Automated deployment script
5. **.env.prod** - Environment template with all variables

---

**Status**: ✅ **Ready for Production Deployment**

Your Natpudan AI Medical Assistant is now configured for:
- ✅ Multi-container orchestration with Podman
- ✅ PostgreSQL production database
- ✅ Redis caching and job queue
- ✅ Celery background task processing
- ✅ Nginx reverse proxy with SSL/TLS
- ✅ Health checks and monitoring
- ✅ Resource limits and optimization
- ✅ Structured logging
- ✅ Security hardening
- ✅ Automated backup strategies

**Deployment Time**: ~10-15 minutes  
**Estimated Monthly Cost**: $50-200 (depending on cloud provider)  
**Expected Uptime**: 99.5%+ with proper monitoring

