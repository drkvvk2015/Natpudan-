# [WRENCH] Fix White Screen Issue - Step by Step

## [OK] Both Services Are Running!

- **Backend:** https://127.0.0.1:8000 
- **Frontend:** https://127.0.0.1:5173 

## [EMOJI] Why You See White Screen

The white screen is caused by **browser security blocking the self-signed SSL certificates**. You need to accept the certificates for both URLs.

## [EMOJI] Follow These Steps EXACTLY:

### Step 1: Accept Backend Certificate First

1. Open a NEW browser tab
2. Go to: **https://127.0.0.1:8000/health**
3. You'll see a security warning: **"Your connection is not private"** or **"NET::ERR_CERT_AUTHORITY_INVALID"**
4. Click **"Advanced"** or **"Show details"**
5. Click **"Proceed to 127.0.0.1 (unsafe)"** or **"Accept the risk and continue"**
6. You should see: `{"status":"healthy","service":"api","timestamp":"..."}`

### Step 2: Accept Frontend Certificate

1. Open ANOTHER new browser tab
2. Go to: **https://127.0.0.1:5173**
3. You'll see the SAME security warning again (this is normal!)
4. Click **"Advanced"** again
5. Click **"Proceed to 127.0.0.1 (unsafe)"** again
6. The app should now load!

### Step 3: If Still White Screen

1. Press **F12** to open Developer Tools
2. Click the **Console** tab
3. Look for errors (usually red text)
4. Take a screenshot and share it

## [EMOJI] Quick Diagnostics

### Test 1: Check if backend is accessible
Open in browser: https://127.0.0.1:8000/docs
- Should show Swagger API documentation

### Test 2: Check if frontend HTML loads
Open in browser: view-source:https://127.0.0.1:5173/
- Should show HTML with `<div id="root"></div>`

### Test 3: Check JavaScript console
1. Go to: https://127.0.0.1:5173
2. Press F12
3. Look for errors in Console tab

## [EMOJI] Common Issues & Solutions

### Issue: "ERR_CERT_AUTHORITY_INVALID"
**Solution:** Follow Step 1 and Step 2 above - you MUST accept certificates for BOTH URLs

### Issue: "Network Error" or "Failed to fetch"
**Solution:** 
1. Make sure backend is running (check https://127.0.0.1:8000/health)
2. Make sure you accepted BOTH certificates
3. Check browser console for CORS errors

### Issue: React errors in console
**Solution:**
1. Clear browser cache (Ctrl+Shift+Delete)
2. Do a hard refresh (Ctrl+F5)
3. Try in incognito/private mode

### Issue: Services not running
**Solution:**
```powershell
# Check what's running
Get-NetTCPConnection -LocalPort 8000,5173 | Select-Object LocalPort, State

# If nothing, start services:
# Terminal 1:
cd D:\Users\CNSHO\Documents\GitHub\Natpudan-\backend
D:/Users/CNSHO/Documents/GitHub/Natpudan-/.venv/Scripts/python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --ssl-keyfile certs\key.pem --ssl-certfile certs\cert.pem

# Terminal 2:
cd D:\Users\CNSHO\Documents\GitHub\Natpudan-\frontend
npx vite --host 127.0.0.1 --port 5173
```

## [EMOJI] What Should Happen

After accepting both certificates, you should see:
1. **Login page** with email/password fields
2. **Register link** at the bottom
3. **Google/GitHub OAuth buttons** (if configured)

##  If You Still See White Screen

1. Take screenshot of browser with F12 console open
2. Check these URLs work:
   - https://127.0.0.1:8000/health (should show JSON)
   - https://127.0.0.1:8000/docs (should show Swagger UI)
   - https://127.0.0.1:5173 (should show login page)

##  Pro Tips

- **Use Chrome/Edge:** Best compatibility with self-signed certs
- **Incognito Mode:** Fresh start without cache issues
- **Clear Cache:** If you see old errors
- **Check Console:** Press F12, Console tab shows real errors

---

## [OK] Verification Checklist

- [ ] Opened https://127.0.0.1:8000/health and accepted certificate
- [ ] Saw {"status":"healthy"} response
- [ ] Opened https://127.0.0.1:5173 and accepted certificate
- [ ] Login page is now visible
- [ ] No errors in F12 console

**Once all checked, the app should work!** [EMOJI]
