# Google Login Fix - Issue Resolution

## Issues Identified

### 1. **Wrong API Port Configuration**
- **Problem**: Frontend `.env` had `VITE_API_BASE_URL=http://127.0.0.1:8000`
- **Reality**: Backend is running on port **8001**
- **Impact**: All API calls were failing with "Failed to fetch"
- **Fix**: Updated frontend `.env` to use port 8001

### 2. **Missing redirect_uri in OAuth Callback**
- **Problem**: OAuth callback wasn't sending `redirect_uri` to backend
- **Impact**: Backend couldn't verify the redirect URI with Google
- **Fix**: Added `redirect_uri` parameter to OAuth callback request

### 3. **OAuth Flow Calling Backend Twice**
- **Problem**: Component was calling backend twice - once without role, once with role
- **Impact**: First call failed because backend requires `role` parameter
- **Fix**: Refactored to show role selection BEFORE making API call

## Files Modified

### 1. `frontend/.env`
```diff
- VITE_API_BASE_URL=http://127.0.0.1:8000
- VITE_WS_URL=ws://127.0.0.1:8000
+ VITE_API_BASE_URL=http://127.0.0.1:8001
+ VITE_WS_URL=ws://127.0.0.1:8001
```

### 2. `frontend/src/pages/OAuthCallback.tsx`
**Changed OAuth flow to:**
1. Extract code and state from URL
2. Show role selection UI immediately
3. When user clicks "Continue", make single API call with:
   - code
   - provider
   - redirect_uri
   - state
   - **role** (selected by user)

## Testing the Fix

### Prerequisites
1. Backend running on port 8001 [OK]
2. Frontend running on port 5173 [OK]
3. Google OAuth credentials configured [OK]

### Test Steps
1. Go to http://localhost:5173/login
2. Click "Continue with Google"
3. Should redirect to Google login
4. After Google authentication, should return to app
5. Should show "Select Your Role" screen
6. Select a role (Staff/Doctor/Admin)
7. Click "Continue as [Role]"
8. Should successfully log in and redirect to dashboard

## Important Notes

### Google Cloud Console Configuration
**CRITICAL**: Ensure your Google OAuth app has the correct redirect URI:
- Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
- Find your OAuth 2.0 Client ID: `954638857557-oefbgk5bgj6ctutd3n27elb9ta73jbi6.apps.googleusercontent.com`
- Under "Authorized redirect URIs", ensure it includes:
  - `http://localhost:5173/auth/callback`

If this is not configured, Google will reject the redirect.

### Environment Variables
Backend `.env` has valid Google OAuth credentials:
```
GOOGLE_CLIENT_ID=954638857557-oefbgk5bgj6ctutd3n27elb9ta73jbi6.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
```

### Restart Required
After modifying `.env` files, you need to restart the servers:
```powershell
# Stop both servers (Ctrl+C in their terminals)
# Then run:
.\START_APP.ps1
```

## OAuth Flow Diagram

```
User clicks "Continue with Google"
    [DOWN]
Frontend calls: GET /api/auth/oauth/google/url?redirect_uri=...
    [DOWN]
Backend returns Google authorization URL
    [DOWN]
Frontend redirects to Google
    [DOWN]
User authenticates with Google
    [DOWN]
Google redirects back to: http://localhost:5173/auth/callback?code=...&state=...
    [DOWN]
Frontend shows "Select Your Role" UI
    [DOWN]
User selects role and clicks "Continue"
    [DOWN]
Frontend calls: POST /api/auth/oauth/callback
    with { code, provider, redirect_uri, state, role }
    [DOWN]
Backend exchanges code for Google access token
    [DOWN]
Backend gets user info from Google
    [DOWN]
Backend creates/updates user in database with selected role
    [DOWN]
Backend generates JWT token
    [DOWN]
Backend returns { access_token, user }
    [DOWN]
Frontend stores token and redirects to dashboard
```

## Status
- [OK] Port mismatch fixed
- [OK] redirect_uri parameter added
- [OK] OAuth flow refactored to single API call
- [EMOJI] **Need to restart frontend to load new .env**
- [EMOJI] **Need to verify Google Cloud Console redirect URI configuration**

## Next Steps
1. Restart frontend server to load updated `.env` file
2. Test Google login flow
3. If still fails, verify Google Cloud Console redirect URI
4. Check browser console and backend logs for detailed error messages
