# [WRENCH] Fix Port 8001 Error - Browser Cache Issue

**Problem**: Frontend is trying to connect to port 8001, but backend runs on port 8000.

**Cause**: Browser has cached old JavaScript files that reference port 8001.

---

## [EMOJI] Quick Fix (Do This Now)

### **Step 1: Clear Browser Cache**

#### **Chrome/Edge**
1. Press `Ctrl + Shift + Delete`
2. Select "Cached images and files"
3. Click "Clear data"

#### **Or Use Hard Refresh**
1. Press `Ctrl + Shift + R` (force reload without cache)
2. Or `Ctrl + F5`

---

### **Step 2: Restart Application**

```powershell
# Stop all services
Get-Job | Stop-Job
Get-Job | Remove-Job

# Restart
.\start-app.ps1
```

---

### **Step 3: Clear Vite Build Cache**

```powershell
# Delete Vite cache
cd frontend
Remove-Item -Recurse -Force node_modules\.vite -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue

# Restart frontend
npm run dev
```

---

## [OK] Verify Fix

1. Open browser DevTools (`F12`)
2. Go to Network tab
3. Check requests are going to `http://127.0.0.1:8000` (NOT 8001)
4. Try logging in again

---

## [EMOJI] Prevent This Issue

### **Method 1: Disable Cache in DevTools**
1. Open DevTools (`F12`)
2. Go to Network tab
3. Check "Disable cache" checkbox
4. Keep DevTools open while developing

### **Method 2: Use Incognito/Private Mode**
- No cache, fresh start every time
- `Ctrl + Shift + N` (Chrome) or `Ctrl + Shift + P` (Firefox)

---

## [EMOJI] Why This Happened

The error logs show:
```
:8001/api/auth/login:1  Failed to load resource: net::ERR_CONNECTION_REFUSED
```

But your `.env` file says:
```
VITE_API_BASE_URL=http://127.0.0.1:8000  [OK] Correct
```

**Reason**: Browser cached the old JavaScript bundle when port was 8001. Even though you changed `.env`, the cached JS still has the old value.

---

## [EMOJI] After Clearing Cache

You should see:
```
[OK] :8000/api/auth/login - Status 200 OK
[OK] Login successful
[OK] Redirected to dashboard
```

Not:
```
[X] :8001/api/auth/login - ERR_CONNECTION_REFUSED
```
