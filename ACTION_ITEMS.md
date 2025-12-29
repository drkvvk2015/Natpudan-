# 🎯 PODMAN PRODUCTION DEPLOYMENT - ACTION ITEMS

**Current Status**: ✅ All configurations ready  
**Deployment Method**: Podman (Docker-compatible container orchestration)  
**Estimated Setup Time**: 90 minutes for full production

---

## 📋 IMMEDIATE ACTION ITEMS (Do These First)

### 1️⃣ Configure Environment File (5 minutes)

```powershell
# Copy production template
Copy-Item .env.prod -Destination .env.prod.local

# Edit the file
notepad .env.prod.local
```

**Required Changes** (Don't skip!):

```bash
# Line 11: GENERATE A NEW SECRET KEY (256 chars)
SECRET_KEY=<RUN THIS POWERSHELL COMMAND BELOW>

# Line 16: STRONG DATABASE PASSWORD
POSTGRES_PASSWORD=<ChangeThisTo20+CharsWithNumbers!Symbols>

# Line 42: YOUR ACTUAL OPENAI API KEY
OPENAI_API_KEY=sk-proj-<your-actual-key-here>

# Line 64: YOUR DOMAIN
FRONTEND_URL=https://yourdomain.com
VITE_API_BASE_URL=https://api.yourdomain.com
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Line 75: DEBUG MODE (MUST be false for production!)
DEBUG=false
```

**Generate SECRET_KEY** (run in PowerShell):
```powershell
$secret = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((1..256 | ForEach-Object { [char](Get-Random -Minimum 33 -Maximum 126) }) -join ''))
Write-Host "SECRET_KEY=$secret" | clip
# Now paste into .env.prod.local
```

---

### 2️⃣ Quick Test - Local Deployment (10 minutes)

Run the deployment script to test everything locally:

```powershell
# Activate environment
.\.venv\Scripts\Activate.ps1

# Run deployment for LOCAL testing first
.\podman-deploy.ps1 -DeploymentMode local -EnvFile .env.prod.local

# This will:
# ✅ Validate Podman installation
# ✅ Build container images
# ✅ Start all 7 services
# ✅ Wait for health checks
# ✅ Display access URLs
```

**Expected Output**:
```
✅ All prerequisites met!
✅ Images built successfully
✅ Services started
✅ All services are healthy
✅ Deployment Complete!

Access the application:
  Frontend:      http://127.0.0.1:3000
  Backend API:   http://127.0.0.1:8000
  API Docs:      http://127.0.0.1:8000/docs
  Flower (Jobs): http://127.0.0.1:5555
  Health:        http://127.0.0.1:8000/health
```

---

### 3️⃣ Verify Services Running (5 minutes)

```powershell
# Check all services
podman-compose ps

# Expected: All services showing "running" with "healthy"

# View backend logs
podman-compose logs backend -n 20

# Test API endpoint
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing
$response.Content | ConvertFrom-Json | ConvertTo-Json
```

---

### 4️⃣ Open in Browser (5 minutes)

```powershell
# Open frontend
Start-Process http://127.0.0.1:3000

# You should see:
# ✅ Login page loads
# ✅ Backend connection shows "ONLINE" (not offline!)
# ✅ No console errors in browser DevTools
```

---

## 🚀 NEXT STEPS FOR PRODUCTION (After Local Testing Works)

### Step 5: Prepare Domain & SSL (30 minutes)

**Option A: Let's Encrypt (FREE, Recommended)**
```powershell
# Install Certbot
choco install certbot

# Get certificate
certbot certonly --standalone -d yourdomain.com -d api.yourdomain.com

# Copy to nginx folder
Copy-Item "C:\Certbot\live\yourdomain.com\fullchain.pem" nginx/ssl/cert.pem
Copy-Item "C:\Certbot\live\yourdomain.com\privkey.pem" nginx/ssl/key.pem
Copy-Item "C:\Certbot\live\yourdomain.com\chain.pem" nginx/ssl/chain.pem
```

**Option B: Paid Certificate**
```powershell
# Download your certificate from provider
# Place in nginx/ssl/:
# - cert.pem (certificate)
# - key.pem (private key)
# - chain.pem (intermediate certificates)
```

---

### Step 6: Production Deployment (20 minutes)

```powershell
# Update environment file with production values
notepad .env.prod.local
# Change:
# - ENVIRONMENT=production
# - DEBUG=false
# - FRONTEND_URL=https://yourdomain.com
# - VITE_API_BASE_URL=https://api.yourdomain.com

# Deploy to production
.\podman-deploy.ps1 -DeploymentMode production -EnvFile .env.prod.local

# Verify
podman-compose ps
curl https://yourdomain.com/health --insecure  # --insecure only for testing
```

---

### Step 7: Configure Monitoring (30 minutes)

**Option A: Simple (Free)**
```bash
# Set up basic health check monitoring
# Check /health endpoint every 5 minutes
# Alert if services down
```

**Option B: Advanced (Optional)**
```bash
# Install Prometheus + Grafana for metrics
# Install Sentry for error tracking
# See PRODUCTION_DEPLOYMENT_PODMAN.md for setup
```

---

### Step 8: Set Up Backups (20 minutes)

```powershell
# Create daily backup script
@"
# Run daily at 2 AM
`$timestamp = Get-Date -Format "yyyy-MM-dd-HHmmss"
podman exec physician-ai-db pg_dump -U physician_user -d physician_ai > "backup-`$timestamp.sql"
gzip "backup-`$timestamp.sql"
# Upload to cloud storage (AWS S3, Azure Blob, etc.)
"@ | Out-File backup.ps1

# Schedule with Task Scheduler
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File C:\path\to\backup.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At 02:00
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "NatpudanBackup" -Description "Daily database backup"
```

---

## 📊 VERIFICATION CHECKLIST

After each deployment step, verify:

### After Local Deployment
- [ ] All 7 services running (`podman-compose ps`)
- [ ] Backend health check passes (`curl http://127.0.0.1:8000/health`)
- [ ] Frontend loads at `http://127.0.0.1:3000`
- [ ] Login page shows "Backend: ONLINE"
- [ ] Flower dashboard at `http://127.0.0.1:5555`

### After Production Deployment
- [ ] All services running on production server
- [ ] SSL/TLS certificate valid
- [ ] Domain resolves correctly
- [ ] HTTPS works without warnings
- [ ] API endpoints respond with 200/401 (not 500)
- [ ] Database backups created successfully
- [ ] Monitoring system activated

---

## ⚠️ CRITICAL REMINDERS

🚨 **DO NOT FORGET:**

1. **SECRET_KEY** - Must be randomly generated (not "changeme")
   - If you use default, anyone can forge JWT tokens!
   
2. **DEBUG=false** - Must be set in production
   - Debug=true exposes sensitive information!

3. **Database Password** - Must be strong (20+ chars, mixed case, numbers, symbols)
   - Weak password = database breach!

4. **SSL Certificate** - Must be valid and auto-renewed
   - Expired certificate = users can't access!

5. **Backups** - Must be tested and off-site
   - No backups = data loss when server fails!

---

## 📚 IMPORTANT FILES TO READ

In Order:
1. **PODMAN_PRODUCTION_QUICK_START.md** (10 min read) - Overview
2. **DEPLOYMENT_STATUS.md** (15 min read) - Detailed checklist
3. **PRODUCTION_DEPLOYMENT_PODMAN.md** (30 min read) - Complete guide

---

## 🎯 SUCCESS CRITERIA

Your deployment is successful when:

✅ **Services**
- [ ] All 7 services running and healthy
- [ ] Health check endpoints responding
- [ ] Database initialized with tables
- [ ] Celery workers processing tasks

✅ **Frontend**
- [ ] Loads without errors
- [ ] Shows "Backend: ONLINE"
- [ ] Login page accessible
- [ ] API calls work (check browser DevTools)

✅ **Backend**
- [ ] API responds to requests
- [ ] Knowledge base loads on first request
- [ ] OpenAI integration working
- [ ] Logs clean (no ERROR/CRITICAL messages)

✅ **Security**
- [ ] SSL/TLS certificate valid
- [ ] CORS configured correctly
- [ ] Rate limiting active
- [ ] Secrets not exposed in logs

✅ **Operations**
- [ ] Health checks passing
- [ ] Logs rotating (not growing forever)
- [ ] Backups created and verified
- [ ] Monitoring system active

---

## 🆘 TROUBLESHOOTING QUICK FIXES

### Services won't start
```powershell
podman-compose logs backend
# Look for error messages, fix, then:
podman-compose down -v
podman-compose build --no-cache
podman-compose up -d
```

### Backend says "Backend Offline" in login
```powershell
# Check if backend is running
curl http://127.0.0.1:8000/health

# If not running:
podman-compose restart backend

# Check logs for errors:
podman logs physician-ai-backend
```

### High memory usage
```powershell
podman stats

# Reduce Celery workers in docker-compose.yml:
# Change: concurrency=4
# To: concurrency=2
```

### Cannot connect to database
```powershell
podman logs physician-ai-db

# Check password matches in .env:
grep POSTGRES_PASSWORD .env.prod.local
```

See full troubleshooting in [PRODUCTION_DEPLOYMENT_PODMAN.md](./PRODUCTION_DEPLOYMENT_PODMAN.md)

---

## ⏱️ ESTIMATED TIMELINE

| Step | Time | Task |
|------|------|------|
| 1 | 5 min | Configure .env.prod.local |
| 2 | 10 min | Run local deployment |
| 3 | 5 min | Verify services |
| 4 | 5 min | Test in browser |
| **Subtotal** | **25 min** | **Local Testing Complete** |
| 5 | 30 min | Get SSL certificate |
| 6 | 20 min | Production deployment |
| 7 | 30 min | Monitoring setup |
| 8 | 20 min | Backups configuration |
| **TOTAL** | **125 min** | **Full Production Ready** |

---

## 🎓 DOCUMENTATION REFERENCE

| Document | Purpose | When to Read |
|----------|---------|--------------|
| [PODMAN_PRODUCTION_QUICK_START.md](./PODMAN_PRODUCTION_QUICK_START.md) | Quick overview | Before starting |
| [DEPLOYMENT_STATUS.md](./DEPLOYMENT_STATUS.md) | Full checklist | Reference during |
| [PRODUCTION_DEPLOYMENT_PODMAN.md](./PRODUCTION_DEPLOYMENT_PODMAN.md) | Deep dive | For details |
| [docker-compose.yml](./docker-compose.yml) | Service config | For customization |
| [nginx/nginx.conf](./nginx/nginx.conf) | Proxy config | For SSL/domain setup |
| [.env.prod](../.env.prod) | Environment template | For configuration |

---

## ✅ YOU'RE READY!

**Status**: All files configured, scripts ready, documentation complete.

**Next Action**: Run this command right now:
```powershell
.\podman-deploy.ps1 -DeploymentMode local -EnvFile .env.prod.local
```

**Questions?** See [PRODUCTION_DEPLOYMENT_PODMAN.md](./PRODUCTION_DEPLOYMENT_PODMAN.md) → "Troubleshooting" section

---

**Let's deploy! 🚀**

