# Natpudan v2.0 Enterprise - Deployment & Testing Guide

## Contents
1. Pre-Deployment Checklist
2. Local Development Setup
3. Testing Strategy
4. API Testing Guide
5. Database Setup
6. Production Deployment
7. Troubleshooting Guide

---

## 1. Pre-Deployment Checklist

### Backend Requirements
- [ ] Python 3.9+ installed
- [ ] All dependencies in `requirements.txt` installed
- [ ] PostgreSQL or SQLite database available
- [ ] OpenAI API key obtained
- [ ] JWT_SECRET_KEY configured (min 32 chars)
- [ ] CORS_ORIGINS configured for frontend URL
- [ ] All optional features in `.env` configured

### Frontend Requirements
- [ ] Node.js 16+ installed
- [ ] npm or yarn available
- [ ] All dev dependencies installed (`npm install`)
- [ ] Build process tested locally (`npm run build`)
- [ ] D3.js and Recharts installed for visualizations

### Infrastructure
- [ ] SSL/TLS certificates (production only)
- [ ] Firewall rules configured
- [ ] Database backups enabled
- [ ] Email/SMS service credentials obtained (if using notifications)
- [ ] Monitor/logging service account created

---

## 2. Local Development Setup

### Step 1: Clone & Setup Backend

```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
cp .env.template .env
# Edit .env with your values:
nano .env  # or use your editor

# Required for minimal setup:
export OPENAI_API_KEY=sk-your-key
export JWT_SECRET_KEY=your-secret-key-min-32-chars
```

### Step 3: Initialize Database

```bash
# This runs automatically on app startup via init_db()
# But you can test it with:
python -c "from app.database import init_db; init_db()"

# Verify tables created:
sqlite3 data/natpudan.db ".tables"
```

### Step 4: Start Backend Server

```bash
# From backend directory:
cd backend
uvicorn app.main:app --reload --port 8000

# Output should show:
# INFO:     Application startup complete [STARTED] Natpudan AI Medical Assistant...
# [OK] Database initialized successfully
# [OK] OpenAI API configured
# [OK] Knowledge base loaded (XXXX documents)
# [OK] Wearable device sync worker started (5-min intervals)
```

### Step 5: Setup Frontend

```bash
cd frontend
npm install

# Create .env.local
cat > .env.local << EOF
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
EOF

# Start dev server
npm start
# Should open http://localhost:3000
```

### Step 6: Test Basic Flow

1. Navigate to http://localhost:3000
2. Login (use demo credentials or register new user)
3. Go to Dashboard
4. Verify all menu items appear (including new features)
5. Click each new feature route to verify loading

---

## 3. Testing Strategy

### Unit Tests (Backend)

```bash
cd backend

# Run all tests
pytest -v

# Run specific test file
pytest tests/test_voice_transcriber.py -v

# Run with coverage
pytest --cov=app tests/

# Test individual services
pytest tests/services/test_readmission_predictor.py
pytest tests/services/test_voice_transcriber.py
pytest tests/services/test_wearable_sync.py
```

### Integration Tests

```bash
# Test API endpoints
pytest tests/api/test_voice.py -v
pytest tests/api/test_predictions.py -v
pytest tests/api/test_wearable_auth.py -v

# Test database interactions
pytest tests/integration/test_voice_recording_flow.py -v
pytest tests/integration/test_readmission_pipeline.py -v
```

### Manual Testing (Postman/curl)

See "API Testing Guide" below

### Frontend Tests

```bash
cd frontend

# Run Jest tests
npm test

# E2E tests with Playwright/Cypress (if configured)
npm run test:e2e

# Visual regression tests
npm run test:visual
```

### Performance Testing

```bash
# Backend load testing
# Using Apache Bench or wrk:
ab -n 1000 -c 10 http://localhost:8000/health

# Voice transcription latency (30s audio):
# Expected: < 5 seconds

# Model prediction latency:
# Expected: < 100ms for readmission prediction

# Frontend bundle size:
npm run build && npm run analyze
# Expected: main bundle < 500KB
```

---

## 4. API Testing Guide

### Quick Reference Commands

All commands assume `BASE_URL=http://localhost:8000`

#### 1. Voice Documentation

```bash
# Upload audio file (recording.wav required)
curl -X POST -F "file=@/path/to/recording.wav" \
  $BASE_URL/api/voice/upload

# Response:
{
  "success": true,
  "recording_id": "uuid",
  "raw_transcription": "...",
  "medical_entities": {...},
  "soap_note_preview": {...}
}

# Generate discharge summary
curl -X POST $BASE_URL/api/voice/generate-documentation \
  -H "Content-Type: application/json" \
  -d '{
    "recording_id": "uuid",
    "edited_transcription": "Updated text if needed"
  }'
```

#### 2. Readmission Prediction

```bash
# Predict readmission risk
curl -X POST $BASE_URL/api/predictions/readmission-risk \
  -H "Content-Type: application/json" \
  -d '{"patient_intake_id": 1}'

# Get model statistics
curl $BASE_URL/api/predictions/model-stats

# Get high-risk patients
curl $BASE_URL/api/predictions/high-risk-patients

# Get alerts for patient
curl $BASE_URL/api/predictions/patient/1/alerts

# Acknowledge alert
curl -X POST $BASE_URL/api/predictions/alerts/1/acknowledge
```

#### 3. Wearable Integration

```bash
# Get connected devices
curl $BASE_URL/api/wearable/devices

# Get Fitbit auth URL
curl $BASE_URL/api/wearable/auth/fitbit/url

# Manual sync
curl -X POST $BASE_URL/api/wearable/sync-now

# Get latest vitals
curl $BASE_URL/api/wearable/latest
```

#### 4. Knowledge Graph

```bash
# Search concept
curl "$BASE_URL/api/medical/knowledge/graph/search?concept=diabetes"

# Export D3 format
curl $BASE_URL/api/medical/knowledge/graph/export/d3

# Get node details
curl $BASE_URL/api/medical/knowledge/graph/node/disease_001

# Find paths between concepts
curl -X POST $BASE_URL/api/medical/knowledge/graph/paths \
  -H "Content-Type: application/json" \
  -d '{"source": "diabetes", "target": "kidney_disease"}'

# Graph statistics
curl $BASE_URL/api/medical/knowledge/graph/stats
```

#### 5. Futuristic Features

```bash
# XAI Explanation
curl -X POST $BASE_URL/api/features/xai/explain-diagnosis \
  -d '{"patient_id": 1, "diagnosis": "diabetes"}'

# Treatment Recommendations
curl -X POST $BASE_URL/api/features/treatment-recommender/recommend \
  -d '{"diagnosis": "hypertension", "patient_age": 65}'

# Discharge Planning
curl -X POST $BASE_URL/api/features/discharge-planning/generate-plan \
  -d '{"patient_id": 1, "discharge_summary_id": 5}'

# Clinical Trials
curl -X POST $BASE_URL/api/features/clinical-trials/find-matches \
  -d '{"diagnosis": "cancer", "cancer_type": "melanoma"}'

# Check all features status
curl $BASE_URL/api/features/status
```

#### 6. FHIR Export

```bash
# Export patient as FHIR Bundle
curl $BASE_URL/api/features/fhir-connector/export-patient/1 \
  -H "Accept: application/fhir+json"

# Response is FHIR Bundle JSON
```

---

## 5. Database Setup

### SQLite (Development)

```bash
# Already created by app on startup
# Located at: backend/data/natpudan.db

# Access directly:
sqlite3 backend/data/natpudan.db

# Useful queries:
sqlite> SELECT * FROM voice_recording;
sqlite> SELECT * FROM wearable_device_data;
sqlite> SELECT * FROM alert;
sqlite> SELECT * FROM patient_intake LIMIT 5;
```

### PostgreSQL (Production)

```bash
# Create database
createdb natpudan_prod

# Update .env
DATABASE_URL=postgresql://user:password@localhost:5432/natpudan_prod

# Test connection
python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://user:password@localhost:5432/natpudan_prod'); engine.connect(); print('Connected!')"

# Tables auto-create on app startup
```

### Backup Strategy

```bash
# SQLite backup (nightly via cron)
sqlite3 data/natpudan.db ".backup '/backups/natpudan_$(date +%Y%m%d).db'"

# PostgreSQL backup (nightly via cron)
pg_dump natpudan_prod | gzip > /backups/natpudan_$(date +%Y%m%d).sql.gz

# Restore
gunzip < /backups/natpudan_20240418.sql.gz | psql natpudan_prod
```

---

## 6. Production Deployment

### Option A: Docker (Recommended)

```bash
# Build images
docker build -f backend/Dockerfile -t natpudan-backend:v2.0 .
docker build -f frontend/Dockerfile -t natpudan-frontend:v2.0 .

# Tag for registry
docker tag natpudan-backend:v2.0 your-registry/natpudan-backend:v2.0
docker tag natpudan-frontend:v2.0 your-registry/natpudan-frontend:v2.0

# Push
docker push your-registry/natpudan-backend:v2.0
docker push your-registry/natpudan-frontend:v2.0

# Deploy with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

### Option B: Kubernetes

```bash
# Build and push images (see Docker option above)

# Deploy
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# Verify
kubectl get pods -n natpudan
kubectl get svc -n natpudan

# Logs
kubectl logs -n natpudan deployment/natpudan-backend -f
```

### Option C: Traditional Server

```bash
# On Ubuntu/Debian server:

# Install dependencies
sudo apt-get update
sudo apt-get install -y python3.10 python3-pip nodejs npm postgresql

# Clone repo
git clone https://github.com/your-org/natpudan.git
cd natpudan

# Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup frontend
cd ../frontend
npm install
npm run build

# Setup systemd service
sudo cp natpudan-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable natpudan-backend
sudo systemctl start natpudan-backend

# Setup nginx reverse proxy
sudo apt-get install -y nginx
sudo cp nginx.conf /etc/nginx/sites-available/natpudan
sudo ln -s /etc/nginx/sites-available/natpudan /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Environment Variables (Production)

```bash
# Critical security settings:
APP_ENV=production
DEBUG=false
LOG_LEVEL=WARNING

# Database with strong credentials
DATABASE_URL=postgresql://prod_user:strong_password@db-server:5432/natpudan_prod

# JWT with strong secret (at least 64 chars)
JWT_SECRET_KEY=your-very-long-random-secret-min-64-chars

# CORS restricted to your domain
CORS_ORIGINS=https://app.natpudan.example.com,https://admin.natpudan.example.com

# Enable production security features
HIPAA_ENCRYPTION_AT_REST=true
HIPAA_AUDIT_LOGGING=true

# Monitoring
SENTRY_DSN=https://your-key@sentry.io/project
NEW_RELIC_LICENSE_KEY=your_key
```

### SSL/TLS with Let's Encrypt

```bash
# Install certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --nginx -d app.natpudan.example.com

# Auto-renew
sudo systemctl enable certbot.timer
```

### Performance Optimization

```bash
# Enable caching
# In main.py, add:
@app.middleware("http")
async def add_cache_header(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/static"):
        response.headers["Cache-Control"] = "public, max-age=86400"
    return response

# Database connection pooling
# Already configured in backend/app/database.py
```

---

## 7. Troubleshooting Guide

### Backend Issues

#### "No OpenAI API Key" but key is set
```bash
# Check env variable loaded
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"

# Verify .env file location
ls -la backend/.env

# Source .env manually
set -a
source .env
set +a
```

#### Wearable sync not working
```bash
# Check logs
grep WEARABLE logs/app.log

# Test token validity
curl -H "Authorization: Bearer $FITBIT_TOKEN" \
  https://api.fitbit.com/1/user/-/profile.json

# Check sync interval settings
python -c "from app.models import WearableDeviceAuth; print(WearableDeviceAuth.sync_interval_minutes)"
```

#### Database connection failures
```bash
# Test connection string
python -c "from sqlalchemy import create_engine; engine = create_engine('$DATABASE_URL'); engine.connect()"

# Check database service is running
sudo systemctl status postgresql

# View detailed error
python -c "from app.database import init_db; import sys; init_db()" 2>&1 | tail -20
```

### Frontend Issues

#### Routes not found (404)
```bash
# Verify routes in App.tsx
grep -n "voice-documentation\|wearable-integration\|knowledge-graph" frontend/src/App.tsx

# Rebuild
npm run build

# Clear cache
rm -rf node_modules/.cache
npm start
```

#### API calls failing with 404
```bash
# Check API endpoint exists
curl http://localhost:8000/api/voice/upload -v

# Check backend routing
grep -r "include_router" backend/app/main.py | grep voice

# Test health endpoint
curl http://localhost:8000/health
```

#### Charts not rendering (Knowledge Graph)
```bash
# Check D3 installed
npm list d3

# Verify SVG element created
# Open browser DevTools → Elements tab
# Search for "<svg" tag

# Check browser console for JS errors
# DevTools → Console tab
```

### Database Issues

#### Tables not created
```bash
# Force recreation
python << 'EOF'
from app.database import engine
from app.models import Base

Base.metadata.drop_all(bind=engine)  # WARNING: Destructive!
Base.metadata.create_all(bind=engine)
print("Tables recreated")
EOF

# Verify
sqlite3 data/natpudan.db ".tables"
```

#### Foreign key constraint failures
```bash
# Check for orphaned records
SELECT * FROM voice_recording WHERE patient_intake_id NOT IN (SELECT id FROM patient_intake);

# Fix by deleting orphaned records
DELETE FROM voice_recording WHERE patient_intake_id NOT IN (SELECT id FROM patient_intake);
```

### Performance Issues

#### Slow transcription
```bash
# Check OpenAI quota/rate limiting
# Monitor logs: grep "429\|rate_limit" logs/app.log

# Use local Whisper for faster processing
# Edit app/services/voice_transcriber.py to use local model
```

#### Slow model predictions
```bash
# Check if model training in progress
ps aux | grep "ml_trainer"

# Test prediction latency directly
time python -c "
from app.services.readmission_predictor import get_readmission_predictor
predictor = get_readmission_predictor()
result = predictor.predict_risk(patient_id=1)
print(result)
"
```

---

## Health Checkpoints

✅ **Development**: Backend starts, frontend loads, all routes accessible
✅ **Testing**: API tests pass, database operations work, models train
✅ **Staging**: Full feature test with test data, monitoring working
✅ **Production**: SSL working, monitoring active, backups running, alerts configured

---

**For Issues:** Check logs at `logs/app.log` and `logs/error.log`
**Support:** Refer to INTEGRATION_GUIDE.md for feature-specific docs
