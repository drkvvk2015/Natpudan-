# QUICK START - Backend Manual Setup

If `start-backend.ps1` is not working, use these manual steps:

## Option 1: Using PowerShell (Windows)

```powershell
# 1. Navigate to repo root
cd D:\Users\CNSHO\Documents\GitHub\Natpudan-

# 2. Create Python venv (if not exists)
python -m venv backend\.venv

# 3. Activate venv
backend\.venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r backend\requirements.txt

# If no requirements.txt, install essentials:
# pip install fastapi uvicorn[standard] python-multipart pydantic python-dotenv psutil

# 5. Set PYTHONPATH
$env:PYTHONPATH = "$(Get-Location)\backend"

# 6. Start uvicorn
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Option 2: Using Command Prompt (Windows CMD)

```cmd
REM 1. Navigate to repo
cd D:\Users\CNSHO\Documents\GitHub\Natpudan-

REM 2. Create venv
python -m venv backend\.venv

REM 3. Activate venv
backend\.venv\Scripts\activate.bat

REM 4. Install dependencies
pip install -r backend\requirements.txt

REM 5. Set PYTHONPATH and start
set PYTHONPATH=%cd%\backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Expected Output

When backend starts successfully, you'll see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

Then:
- Open browser: http://127.0.0.1:8000/docs (Swagger UI)
- Test health: http://127.0.0.1:8000/health

## If Backend Fails to Start

Check these common issues:

1. **Port 8000 in use?**
   - Try: `python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001`

2. **Missing dependencies?**
   ```
   pip install fastapi uvicorn[standard] python-multipart pydantic python-dotenv psutil faiss-cpu PyPDF2 python-docx
   ```

3. **Import errors?**
   - Ensure `PYTHONPATH` is set:
     ```
     echo $env:PYTHONPATH  # PowerShell
     echo %PYTHONPATH%     # CMD
     ```
   - Should show backend path

4. **OpenAI API key missing?**
   - Create `backend/.env`:
     ```
     DATABASE_URL=sqlite:///./natpudan.db
     SECRET_KEY=your-secret-key-here
     OPENAI_API_KEY=sk-...
     ```

5. **Database error?**
   - Delete `natpudan.db` (if exists) and restart (it will recreate on startup)

## Testing Upload Endpoint

Once backend is running, in a new PowerShell window:

```powershell
# Test health
curl http://127.0.0.1:8000/health

# Upload file (replace path with actual file)
$filePath = "D:\path\to\file.pdf"
$uri = "http://127.0.0.1:8000/api/upload/document"

$form = @{
    file = Get-Item -Path $filePath
}

Invoke-WebRequest -Uri $uri -Form $form -Method Post | ConvertTo-Json
```

## If Still Failing

Paste the **full error message/stack trace** from the backend console window and I'll implement targeted fixes.
