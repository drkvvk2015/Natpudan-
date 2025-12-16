# Production Environment Configuration Checklist
# Complete ALL items before deploying to production

## 1. Security Configuration

### Secret Key
- [ ] Generate: `openssl rand -hex 32`
- [ ] Add to .env: `SECRET_KEY=<generated-value>`
- [ ] Store securely (do NOT commit to git)

### Database Credentials
- [ ] Change default Postgres password in docker-compose.yml
- [ ] Update DATABASE_URL in .env to match
- [ ] Store credentials in secure location (vault/secrets manager)

### API Keys
- [ ] OpenAI API Key obtained from https://platform.openai.com/api-keys
- [ ] Add to .env: `OPENAI_API_KEY=sk-proj-...`
- [ ] Set appropriate rate limits in OpenAI dashboard

### CORS & Domain
- [ ] Set CORS_ORIGINS to your domain(s): `https://app.example.com`
- [ ] Do NOT use `*` (wildcard) in production
- [ ] Include both with and without www if applicable

### Flower Dashboard
- [ ] Change Flower auth credentials in docker-compose.yml
- [ ] Replace: `--basic_auth=admin:changeme`
- [ ] With: `--basic_auth=admin:<strong-password>`

---

## 2. Environment Variables

### Copy Template
```bash
cd backend
cp .env.production .env
```

### Update These Required Values

| Variable | Current Value | Your Value | Status |
|----------|---|---|---|
| ENVIRONMENT | `production` | - | ✓ |
| DEBUG | `False` | - | ✓ |
| SECRET_KEY | `CHANGE-THIS-...` | Generate with openssl | [ ] |
| OPENAI_API_KEY | `sk-your-openai-api-key-here` | Your key | [ ] |
| DATABASE_URL | `sqlite:///./physician_ai.db` | PostgreSQL URL | [ ] |
| CORS_ORIGINS | `https://yourapp.com` | Your domain | [ ] |
| REDIS_URL | (from docker-compose) | `redis://redis:6379/0` | ✓ |
| CELERY_BROKER_URL | (from docker-compose) | `redis://redis:6379/0` | ✓ |

### Optional but Recommended

| Variable | Recommended Value |
|----------|---|
| ACCESS_TOKEN_EXPIRE_MINUTES | `30` (not 1440) |
| RATE_LIMIT_ENABLED | `True` |
| RATE_LIMIT_CALLS | `100` per 60 seconds |
| LOG_LEVEL | `INFO` (not DEBUG) |
| ENABLE_METRICS | `True` |

---

## 3. Docker Configuration

### Update docker-compose.yml

- [ ] Postgres password (search for `POSTGRES_PASSWORD=`)
  - Change `secure_password` to strong password
- [ ] Database URL in backend environment
  - Matches postgres credentials
- [ ] Flower credentials
  - Change `--basic_auth=admin:changeme`
- [ ] Worker scaling (optional)
  - Backend: `--workers 4` (adjust based on server CPU)
  - Celery: `--concurrency=4` (adjust based on tasks)
- [ ] Resource limits (optional)
  - Add `deploy.resources.limits` for each service

---

## 4. Database Setup

### PostgreSQL
- [ ] Database initialized successfully
- [ ] Schema migrated: `docker-compose exec backend alembic upgrade head`
- [ ] Test connection: `docker-compose exec db psql -U physician_user -d physician_ai -c "SELECT 1"`

### Backups
- [ ] Setup automated daily backups
- [ ] Test restore procedure
- [ ] Store backups in S3/secure location

---

## 5. SSL/TLS Certificates

### Option A: Let's Encrypt (Recommended)
- [ ] Install Certbot on server
- [ ] Generate cert: `certbot certonly --standalone -d yourdomain.com`
- [ ] Copy to `nginx/ssl/`: fullchain.pem, privkey.pem
- [ ] Update nginx.conf with SSL config
- [ ] Setup cert renewal (cron: monthly)

### Option B: Self-Signed
- [ ] Generate cert for testing: `openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/ssl/privkey.pem -out nginx/ssl/fullchain.pem`
- [ ] Update nginx.conf

---

## 6. Server Configuration

### Port & Firewall
- [ ] Port 80 (HTTP) → open
- [ ] Port 443 (HTTPS) → open
- [ ] Port 5555 (Flower) → restricted to admin IPs
- [ ] Other ports → closed

### Resource Allocation
- [ ] At least 4 GB RAM
- [ ] At least 2 CPU cores
- [ ] At least 50 GB disk space
- [ ] Automatic backups enabled

### Logging & Monitoring
- [ ] Setup centralized logging (ELK/Datadog)
- [ ] Setup metrics collection (Prometheus/Datadog)
- [ ] Setup alerting for critical errors
- [ ] Monitor disk usage (alert if > 80%)

---

## 7. Application Testing

### Functional Tests
- [ ] Frontend loads: http://your-domain/
- [ ] Login/Register works
- [ ] Backend API responds: /api/health
- [ ] AI chat functionality works
- [ ] PDF upload works (~2 seconds for 300 pages)
- [ ] Knowledge base search works
- [ ] Drug checker works
- [ ] Patient intake form works

### Performance Tests
- [ ] Load test with 10+ concurrent users
- [ ] PDF upload with 500-page file
- [ ] Monitor memory/CPU during tests
- [ ] Response time < 2 seconds for API calls

### Security Tests
- [ ] SQL injection attempt fails (protected)
- [ ] CORS blocked from unauthorized domains
- [ ] JWT token expiry working
- [ ] Rate limiting working
- [ ] SSL/TLS certificate valid

---

## 8. Pre-Launch Checklist

### Before Going Live
- [ ] All items above checked ✓
- [ ] Code deployed from clean-main2 branch
- [ ] Database backed up
- [ ] Monitoring active
- [ ] Alert recipients configured
- [ ] Runbook created for common issues
- [ ] Support team trained
- [ ] Rollback plan prepared

### Launch Commands
```bash
# Final build
docker-compose build

# Full restart
docker-compose down
docker-compose up -d

# Verify health
docker-compose ps
docker-compose exec backend curl localhost:8000/health

# Monitor logs
docker-compose logs -f
```

---

## 9. Post-Deployment Monitoring

### First 24 Hours
- [ ] Monitor all logs for errors
- [ ] Check CPU/memory usage
- [ ] Verify all endpoints working
- [ ] Test user workflows
- [ ] Monitor Flower for failed tasks

### Weekly
- [ ] Review error logs
- [ ] Check database size
- [ ] Verify backups completed
- [ ] Performance metrics

### Monthly
- [ ] Renew SSL cert if needed
- [ ] Update dependencies/patches
- [ ] Review and optimize queries
- [ ] Capacity planning for growth

---

## Production Access Points

After deployment, access:

| Service | URL | Username | Notes |
|---------|-----|----------|-------|
| Application | `https://yourdomain.com` | - | Main app |
| API | `https://yourdomain.com/api` | - | REST API |
| Docs | `https://yourdomain.com/api/docs` | - | Swagger UI |
| Flower | `http://yourdomain:5555` | admin | Task monitoring |
| Database | Not exposed | - | Via app only |
| Redis | Not exposed | - | Via app only |

---

## Emergency Contacts & Procedures

### Critical Issues
- [ ] On-call contact: ____________________
- [ ] Backup contact: ____________________
- [ ] Vendor contacts (OpenAI, hosting provider): ____________________

### Rollback Procedure
```bash
# If deployment fails:
git checkout previous-version
docker-compose down
docker-compose build
docker-compose up -d
```

---

## Sign-Off

- [ ] All items completed
- [ ] Team reviewed checklist
- [ ] Production ready

**Deployed by:** ____________________  
**Date:** ____________________  
**Version:** ____________________  

---

**For issues or questions, see PRODUCTION_DEPLOYMENT_GUIDE.md**
