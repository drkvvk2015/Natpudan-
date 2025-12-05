# Natpudan AI - Simplified HTTPS Setup

## [OK] What Changed

**Eliminated the problematic Vite proxy** that was causing `ECONNREFUSED` errors. The application now uses direct HTTPS API calls from frontend to backend.

### Key Improvements:
1. **No Proxy Issues** - Frontend makes direct calls to backend API
2. **HTTPS Support** - Both services run on HTTPS with self-signed certificates
3. **Simpler Architecture** - Less configuration, fewer points of failure
4. **Better CORS** - Backend explicitly allows HTTPS frontend origins

## [EMOJI] Quick Start

### Single Command Startup:
```powershell
.\start-https.ps1
```

This script will:
- Generate SSL certificates (if needed)
- Start backend on `https://127.0.0.1:8000`
- Start frontend on `https://127.0.0.1:5173`
- Monitor both services

### Manual Startup:

**Backend:**
```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --ssl-keyfile certs\key.pem --ssl-certfile certs\cert.pem
```

**Frontend:**
```powershell
cd frontend
npx vite --host 127.0.0.1 --port 5173
```

## [EMOJI] Architecture

```
Frontend (https://127.0.0.1:5173)
    [DOWN] Direct HTTPS calls
Backend API (https://127.0.0.1:8000)
```

**Before (Problematic):**
```
Frontend [RIGHT] Vite Proxy [RIGHT] Backend
           [X] ECONNREFUSED
```

**After (Simplified):**
```
Frontend [RIGHT] Direct HTTPS [RIGHT] Backend
           [OK] Works!
```

##  SSL Certificates

Self-signed certificates are generated automatically in:
- `backend/certs/cert.pem`
- `backend/certs/key.pem`
- `frontend/certs/` (copied from backend)

**Browser Warning:** You'll see a security warning about self-signed certificates. This is expected in development. Click "Advanced" and "Proceed" to continue.

##  Access Points

- **Frontend App:** https://127.0.0.1:5173
- **Backend API:** https://127.0.0.1:8000
- **API Documentation:** https://127.0.0.1:8000/docs
- **Health Check:** https://127.0.0.1:8000/health

## [WRENCH] Configuration

### Frontend Environment (`.env`):
```
VITE_API_BASE_URL=https://127.0.0.1:8000
VITE_WS_URL=wss://127.0.0.1:8000
```

### Backend CORS:
Updated `backend/app/main.py` to accept HTTPS frontend origins:
```python
allow_origins=[
    "https://127.0.0.1:5173",
    "https://localhost:5173",
    ...
]
```

### API Client:
Frontend axios client (`src/services/apiClient.ts`) now uses full backend URL:
```typescript
baseURL: import.meta.env.VITE_API_BASE_URL || 'https://127.0.0.1:8000'
```

## [OK] Testing

Test direct API access:
```powershell
# Health check
curl.exe -k https://127.0.0.1:8000/health

# Login attempt
curl.exe -k -X POST https://127.0.0.1:8000/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{"email":"test@test.com","password":"pass"}'
```

## [EMOJI] Troubleshooting

### Port Already in Use
```powershell
# Kill processes on ports
Get-Process | Where-Object { $_.ProcessName -eq 'python' } | Stop-Process -Force
Get-NetTCPConnection -LocalPort 5173 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

### Certificate Issues
Delete certificates and regenerate:
```powershell
Remove-Item backend\certs\*.pem -Force
Remove-Item frontend\certs\*.pem -Force
cd backend
..\.venv\Scripts\python.exe generate_cert.py
Copy-Item certs\*.pem ..\frontend\certs\
```

### CORS Errors
Ensure backend `main.py` includes your frontend URL in `allow_origins` list.

## [EMOJI] Files Modified

1. **`frontend/vite.config.ts`** - Removed proxy configuration
2. **`frontend/src/services/apiClient.ts`** - Direct API calls with full URL
3. **`frontend/.env`** - Full backend URL instead of relative paths
4. **`backend/app/main.py`** - Added HTTPS CORS origins
5. **`backend/generate_cert.py`** - SSL certificate generator
6. **`start-https.ps1`** - Simplified startup script

## [EMOJI] Benefits

[OK] **No More ECONNREFUSED Errors** - Direct connections eliminate proxy issues
[OK] **HTTPS Security** - Encrypted communication between frontend/backend
[OK] **Simpler Debugging** - Direct API calls are easier to trace
[OK] **Production-Like** - HTTPS setup mirrors production environment
[OK] **Fewer Dependencies** - No proxy middleware to configure/maintain

##  Next Steps

1. Open https://127.0.0.1:5173 in your browser
2. Accept the self-signed certificate warning
3. Register a new account or log in
4. All API calls now work directly without proxy errors!

For production deployment, replace self-signed certificates with proper SSL certificates from a certificate authority.
