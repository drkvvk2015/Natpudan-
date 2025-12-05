Development startup checklist

1) Prerequisites
- Python 3.10+ installed and available as `python` in PATH
- Node.js 18+ and npm installed

2) Backend
- Create virtualenv and install dependencies:
  python -m venv .venv
  source .venv/bin/activate  # (or .\.venv\Scripts\Activate.ps1 on Windows)
  pip install --upgrade pip
  if backend/requirements.txt exists:
      pip install -r backend/requirements.txt
  else:
      pip install fastapi uvicorn[standard] python-multipart pydantic python-dotenv psutil

- Optional env file: create `backend/.env` with keys like
  DATABASE_URL=sqlite:///./natpudan.db
  SECRET_KEY=your_secret
  OPENAI_API_KEY=your_openai_key

- Start backend (Unix):
  ./start-dev.sh  # starts backend+frontend
  OR (backend only):
  cd backend
  export PYTHONPATH=$(pwd)
  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

- Start backend (Windows PowerShell):
  .\start-backend.ps1

3) Frontend
- Install dependencies:
  cd frontend
  npm install

- Start frontend:
  npm run dev

- If using the repo orchestrator (Windows):
  .\start-dev.ps1

4) Clearing in-app error logs
- When backend is running, clear in-memory error logs via:
  curl -X POST http://127.0.0.1:8000/api/error-correction/errors/clear

5) Troubleshooting
- If port 8000 is in use, backend will attempt 8001 via start-backend.ps1.
- If vite port (5173) conflicts, change in `frontend/package.json` dev script or start with `PORT=5174 npm run dev`.
- Check backend logs for missing env vars or dependency import errors.

6) Run syntax check
- From repository root:
  python3 scripts/check_python_syntax.py
