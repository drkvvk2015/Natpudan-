# Natpudan v2.0 Enterprise Features - Integration Guide

## Overview

This document provides integration instructions for the 5 quick-win features + 10 futuristic features added to Natpudan.

## Quick-Win Features (Core)

### 1. Voice → Auto Documentation (Feature 1)
**Status:** ✅ Implemented

**Backend Services:**
- `app/services/voice_transcriber.py` - OpenAI Whisper transcription
- `app/services/voice_to_soap.py` - SOAP note generation
- `app/api/voice.py` - REST endpoints

**Frontend:**
- `frontend/src/pages/VoiceDocumentation.tsx` - Full voice recording interface

**Database Models:**
- `VoiceRecording` - Stores recordings and transcriptions

**API Endpoints:**
```
POST /api/voice/upload
  - Upload audio file → transcribe → extract entities
  - Returns: recording_id, transcription, entities, SOAP preview

POST /api/voice/generate-documentation
  - Finalize SOAP note → create discharge summary
  - Returns: discharge_summary_id, final SOAP note

GET /api/voice/recording/{recording_id}
  - Retrieve recording details

DELETE /api/voice/recording/{recording_id}
  - Delete recording
```

**Integration Steps:**
1. Add route to `App.tsx`: `/voice-documentation` → `VoiceDocumentation`
2. Add menu item in `Sidebar.tsx`
3. Configure `OPENAI_API_KEY` in `.env`

---

### 2. Wearable Data Integration (Feature 2)
**Status:** ✅ Implemented

**Backend Services:**
- `app/services/wearable_sync.py` - Fitbit/Apple/Garmin sync
- `app/api/wearable_auth.py` - OAuth flows

**Database Models:**
- `WearableDeviceData` - Time-series measurements
- `WearableDeviceAuth` - OAuth token storage
- `WearableSyncLog` - Audit trail

**Background Worker:**
- Runs every 5 minutes in `main.py/_wearable_sync_loop()`

**API Endpoints:**
```
GET /api/wearable/auth/fitbit/url
  - Returns OAuth auth_url for Fitbit

GET /api/wearable/auth/fitbit/callback
  - Handle OAuth callback

POST /api/wearable/sync-now
  - Manual sync trigger

GET /api/wearable/devices
  - List connected devices

GET /api/wearable/latest
  - Get today's vitals

DELETE /api/wearable/devices/{device_id}
  - Disconnect device
```

**Frontend:**
- `frontend/src/pages/WearableIntegration.tsx` - Device management UI

**Integration Steps:**
1. Add Fitbit OAuth credentials to `.env`
2. Add route: `/wearable-integration` → `WearableIntegration`
3. Add menu item
4. Background worker already auto-starts in main.py

**Environment Variables Needed:**
```
FITBIT_CLIENT_ID=your_fitbit_client_id
FITBIT_CLIENT_SECRET=your_fitbit_secret
FITBIT_REDIRECT_URI=http://localhost:3000/api/wearable/callback/fitbit
```

---

### 3. Predictive Readmission Alerts (Feature 3)
**Status:** ✅ Implemented

**Backend Services:**
- `app/services/readmission_predictor.py` - ML model prediction
- `app/services/ml_trainer.py` - Model training pipeline
- `app/services/alert_generator.py` - Alert creation

**Database Models:**
- `Alert` - Stores all clinical alerts

**API Endpoints:**
```
POST /api/predictions/readmission-risk
  - Input: patient_intake_id
  - Output: risk_score, risk_level, feature_importance, interventions

GET /api/predictions/model-stats
  - Model metrics (accuracy, precision, recall, AUC-ROC)

POST /api/predictions/train-model
  - Manually trigger model retraining

GET /api/predictions/high-risk-patients
  - List patients with readmission risk >= 0.5

GET /api/predictions/patient/{patient_id}/alerts
  - Get alerts for specific patient

POST /api/predictions/alerts/{alert_id}/acknowledge
  - Mark alert as acknowledged

GET /api/predictions/recent-alerts
  - Recent alerts across all patients
```

**Frontend:**
- `frontend/src/components/AlertsWidget.tsx` - Alerts display component

**Integration Steps:**
1. Add `AlertsWidget` to Dashboard: `<AlertsWidget patientId={patientId} />`
2. Import in discharge flow to show readmission risk
3. Model trains automatically on first request (rule-based fallback)

---

### 4. Knowledge Graph Visualization (Feature 4)
**Status:** ✅ Implemented

**Backend:**
- Enhanced `app/services/knowledge_graph.py` with new methods
- New `app/api/knowledge_graph_viz.py` - Visualization endpoints

**API Endpoints:**
```
GET /api/medical/knowledge/graph/export/d3
  - Export graph as D3.js-compatible JSON

GET /api/medical/knowledge/graph/search
  - Search concept → return subgraph

GET /api/medical/knowledge/graph/node/{node_id}
  - Get node details with relationships

GET /api/medical/knowledge/graph/paths
  - Find paths between two concepts

GET /api/medical/knowledge/graph/stats
  - Graph statistics
```

**Frontend:**
- `frontend/src/pages/KnowledgeGraphVisualizer.tsx` - Interactive D3 visualization

**Integration Steps:**
1. Add route: `/knowledge-graph` → `KnowledgeGraphVisualizer`
2. Add menu item
3. Install D3 if not present: `npm install d3`

---

### 5. Ambient Transcription in Consultations (Feature 5)
**Status:** ✅ Implemented

**Backend:**
- `app/services/ambient_transcriber.py` - Real-time transcription
- `app/api/voice_consul.py` - WebSocket endpoint

**API Endpoints:**
```
WebSocket /api/voice/consultation/ws/{conversation_id}
  - Stream audio chunks → receive transcription + entities
  - Messages: {type: "partial_transcript"|"full_transcript"|"entities", data: {...}}

GET /api/voice/consultation/{conversation_id}/summary
  - Get all ambient transcriptions for conversation

POST /api/voice/consultation/{conversation_id}/finalize
  - Mark consultation as complete
```

**Integration Steps:**
1. Create `ConsultationRoom.tsx` with WebSocket audio streaming
2. Add route: `/consultation/{conversationId}` → `ConsultationRoom`
3. WebSocket handler: `AudioCapture.ts` utility for Web Audio API

---

## Top 10 Futuristic Features

### Feature 6: XAI (Explainable AI)
**Service:** `app/services/xai_explainer.py`

```
POST /api/features/xai/explain-diagnosis
  - Input: Patient data, diagnosis
  - Output: Feature importance, uncertainty, confidence scores
```

### Feature 7: AI Treatment Recommender
**Service:** `app/services/ai_treatment_recommender.py`

```
POST /api/features/treatment-recommender/recommend
  - Input: Diagnosis, patient context
  - Output: Primary treatment, alternatives, outcomes, guidelines
```

### Feature 8: Discharge Planning
**Service:** `app/services/discharge_planning_engine.py`

```
POST /api/features/discharge-planning/generate-plan
  - Input: Patient, discharge_summary_id
  - Output: Personalized checklist, timeline, referrals
```

### Feature 9: Clinical Trials Matcher
**Service:** `app/services/clinical_trial_matcher.py`

```
POST /api/features/clinical-trials/find-matches
  - Input: Patient diagnosis, genetics
  - Output: Trial matches, eligibility, enrollment status
```

### Feature 10: Smart Notifications
**Service:** `app/services/smart_notification_engine.py`

```
POST /api/features/notifications/route
  - Input: Alert severity, patient contact info
  - Output: Notification sent via SMS/email/push
```

### Feature 11: FHIR Healthcare Connector
**Service:** `app/services/fhir_connector.py`

```
GET /api/features/fhir-connector/export-patient/{patient_id}
  - Output: FHIR Bundle (JSON)

POST /api/features/fhir-connector/import-hl7
  - Input: HL7v2 message
  - Output: Patient data imported
```

### Feature 12: Real-time Analytics
**Service:** `app/services/realtime_analytics_engine.py`

```
GET /api/features/analytics/disease-heatmap
  - Output: Disease prevalence by location, trends

GET /api/features/analytics/patient-trajectory/{patient_id}
  - Output: Risk predictions (30/90/365-day)
```

### Feature 13: Multi-Language AI
**Service:** `app/services/multilingual_ai.py`

```
POST /api/features/multilingual/translate
  - Input: Medical term, source/target language
  - Output: Translation, confidence

POST /api/features/multilingual/detect-language
  - Input: Text
  - Output: Detected language, confidence
```

### Feature 14: Genomics Integration
**Service:** `app/services/genomics_service.py`

```
POST /api/features/genomics/drug-gene-interactions
  - Input: Medication, genetic variant, ancestry
  - Output: Interaction, dosing adjustment
```

### Feature 15: Public Health Surveillance
**Service:** `app/services/public_health_surveillance.py`

```
GET /api/features/surveillance/outbreak-detection
  - Output: Clusters, epidemic curves, WHO report-ready data
```

---

## Unified Futuristic Features API

All 10+ features are exposed through:
```
GET /api/features/status
  - Returns: All features with operational status, api_version: v2.0-Enterprise
```

See `app/api/futuristic_features.py` for consolidated endpoint definitions.

---

## Environment Configuration

Create/update `.env` with:

```bash
# OpenAI (for Voice & XAI)
OPENAI_API_KEY=sk-your-key

# Fitbit OAuth
FITBIT_CLIENT_ID=your_client_id
FITBIT_CLIENT_SECRET=your_secret
FITBIT_REDIRECT_URI=http://localhost:3000/api/wearable/callback/fitbit

# Notifications
SMS_PROVIDER=twilio  # or sendgrid, aws_sns
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890

EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your_email
EMAIL_PASSWORD=your_app_password

# FHIR Connector (if exposing external API)
FHIR_SERVER_URL=https://fhir-server.example.com
FHIR_AUTH_TOKEN=your_token

# Analytics
GEOLOCATION_API=google_maps  # for disease heatmap
GEOLOCATION_API_KEY=your_key

# Genomics
PHARMACOGENOMICS_API_KEY=your_key
PHARMACOGENOMICS_BASE_URL=https://api.example.com

# Machine Learning
ML_MODEL_PATH=backend/data/models/
ML_TRAINING_DATA_RETENTION_DAYS=365

# Logging
LOG_LEVEL=INFO
```

---

## Frontend Integration Checklist

### 1. Add Routes to `App.tsx`
```typescript
import VoiceDocumentation from "./pages/VoiceDocumentation";
import WearableIntegration from "./pages/WearableIntegration";
import KnowledgeGraphVisualizer from "./pages/KnowledgeGraphVisualizer";

// In router:
<Route path="/voice-documentation" element={<VoiceDocumentation />} />
<Route path="/wearable-integration" element={<WearableIntegration />} />
<Route path="/knowledge-graph" element={<KnowledgeGraphVisualizer />} />
```

### 2. Add Menu Items in `Sidebar.tsx` or Navigation
```typescript
<NavLink to="/voice-documentation" icon={<Mic />}>
  Voice Documentation
</NavLink>
<NavLink to="/wearable-integration" icon={<Watch />}>
  Wearable Devices
</NavLink>
<NavLink to="/knowledge-graph" icon={<NetworkCheck />}>
  Medical Knowledge
</NavLink>
```

### 3. Embed Alerts Widget
```typescript
import AlertsWidget from "../components/AlertsWidget";

// In Dashboard/PatientDetail:
<AlertsWidget patientId={patientId} />

// In AnalyticsDashboard (compact mode):
<AlertsWidget compact={true} />
```

### 4. Install Additional Dependencies
```bash
npm install d3@^7.8.0 recharts
```

---

## Testing Endpoints

### Voice Documentation
```bash
# Record and upload audio
curl -X POST -F "file=@recording.wav" \
  http://localhost:8000/api/voice/upload

# Generate final documentation
curl -X POST http://localhost:8000/api/voice/generate-documentation \
  -H "Content-Type: application/json" \
  -d '{"recording_id": "uuid", "edited_transcription": "text"}'
```

### Readmission Prediction
```bash
# Get risk for patient
curl -X POST http://localhost:8000/api/predictions/readmission-risk \
  -H "Content-Type: application/json" \
  -d '{"patient_intake_id": 1}'

# Get high-risk patients
curl http://localhost:8000/api/predictions/high-risk-patients
```

### Knowledge Graph
```bash
# Search concept
curl "http://localhost:8000/api/medical/knowledge/graph/search?concept=diabetes"

# Export D3
curl http://localhost:8000/api/medical/knowledge/graph/export/d3
```

### Wearable Sync
```bash
# Manual sync
curl -X POST http://localhost:8000/api/wearable/sync-now

# Get devices
curl http://localhost:8000/api/wearable/devices
```

---

## Deployment Notes

### Database Migrations
Models are auto-created on startup via SQLAlchemy `create_all()`. No manual migrations needed.

New models:
- `VoiceRecording`
- `WearableDeviceData`
- `WearableDeviceAuth`
- `WearableSyncLog`
- `Alert`

### Background Workers
Both are auto-started in `main.py` lifespan:
- **Queue worker** (5s interval) - PDF processing
- **Wearable sync worker** (5-min interval) - Device data sync

### Production Recommendations

1. **API Rate Limiting**
   - Voice transcription: 10 requests/min per user
   - Wearable sync: Background worker only, no user-triggered spamming
   - Knowledge graph: 100 queries/min

2. **Data Retention**
   - Voice recordings: Delete after 30 days (HIPAA)
   - Wearable data: 12 months
   - ML training data: 1 year (configurable)

3. **Monitoring**
   - Alert generation: Monitor for false positives
   - Model drift: Retrain readmission model monthly
   - Wearable sync failures: Alert if sync_error_count > 3

4. **Security**
   - Encrypt wearable OAuth tokens at rest
   - HTTPS-only for voice upload
   - Patient consent logging for each feature

---

## Next Steps

1. ✅ Backend services implemented
2. ✅ API routes registered in `main.py`
3. ✅ Frontend components created
4. 🔄 **TODO:** Add routes to frontend router
5. 🔄 **TODO:** Add menu items to navigation
6. 🔄 **TODO:** Configure environment variables
7. 🔄 **TODO:** Integration testing
8. 🔄 **TODO:** Deploy to staging
9. 🔄 **TODO:** Performance tuning
10. 🔄 **TODO:** User training & documentation

---

## Support & Troubleshooting

### Voice transcription fails
- Ensure `OPENAI_API_KEY` is set and valid
- Check file size < 25MB (Whisper limit)
- Verify audio format is supported (wav, mp3, m4a, ogg, flac, aac)

### Wearable sync not working
- Check OAuth tokens not expired
- Verify device is still connected to source account
- Check logs: `tail -f logs/wearable_sync.log`

### Model training error
- Ensure at least 20-30 historical treatment plans in DB
- Check scikit-learn installed: `python -c "import sklearn; print(sklearn.__version__)"`
- Model uses rule-based fallback if training fails

### Knowledge graph visualization slow
- Limit query to max 5-hop distance
- Filter by node type (disease/medication/symptom)
- Use export/cache for static snapshots

---

**Version:** Natpudan v2.0-Enterprise
**Last Updated:** 2026-04-18
**Features:** 5 quick-wins + 10 futuristic = 15 total new capabilities
