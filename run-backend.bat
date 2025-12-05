@echo off
echo Starting Natpudan Backend...
cd /d "%~dp0backend"
call ..\.venv311\Scripts\activate.bat
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
