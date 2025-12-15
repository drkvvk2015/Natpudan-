✅ STARTUP SCRIPTS FIXED - Ready to Use

═══════════════════════════════════════════════════════════════════════════════

All PowerShell startup scripts have been recreated with proper syntax.

WHAT WAS FIXED:
  ✓ Special character encoding issues (emojis, checkmarks)
  ✓ Variable interpolation with colons (${RedisHost}:${RedisPort})
  ✓ Color syntax (@Green → -ForegroundColor Green)
  ✓ Missing braces and try/catch blocks
  ✓ Auto-activation of virtual environment

═══════════════════════════════════════════════════════════════════════════════

QUICK START - 4 Terminal Setup:

Terminal 1 - Redis (Message Broker):
  .\start-redis.ps1
  
Terminal 2 - FastAPI Backend:
  .\start-backend.ps1
  
Terminal 3 - Celery Worker:
  .\start-celery-worker.ps1
  
Terminal 4 - Flower Dashboard:
  .\start-flower.ps1
  
Then open browser to:
  Backend: http://127.0.0.1:8000
  API Docs: http://127.0.0.1:8000/docs
  Flower: http://localhost:5555 (admin/admin)

═══════════════════════════════════════════════════════════════════════════════

REQUIREMENTS:

Before running, ensure:

1. Docker Desktop installed and running (for Redis)
   - Download: https://www.docker.com/products/docker-desktop
   - Or use: choco install docker-desktop (with admin)

2. Python venv created:
   cd backend
   python -m venv venv
   (Scripts will auto-create if missing)

3. Dependencies installed in venv:
   .\venv\Scripts\pip install -r requirements.txt
   (Scripts will auto-install if missing)

═══════════════════════════════════════════════════════════════════════════════

TROUBLESHOOTING:

Issue: "Docker not found"
→ Install Docker Desktop from https://www.docker.com/products/docker-desktop
→ Make sure it's running before starting Redis

Issue: "No module named uvicorn"
→ venv activated successfully, dependencies should install automatically
→ If not, manually run: .\venv\Scripts\pip install -r requirements.txt

Issue: "Redis connection refused"
→ Make sure Terminal 1 (Redis) started successfully
→ Check Docker is running: docker ps
→ Logs: docker logs redis-natpudan

Issue: "Port already in use"
→ Backend (8000): netstat -ano | findstr :8000, then taskkill /PID <pid> /F
→ Redis (6379): docker stop redis-natpudan
→ Flower (5555): netstat -ano | findstr :5555, then taskkill /PID <pid> /F

═══════════════════════════════════════════════════════════════════════════════

SCRIPT DETAILS:

start-backend.ps1
  - Activates venv automatically
  - Runs: python -m uvicorn app.main:app --reload
  - Port: http://127.0.0.1:8000
  - Auto-installs dependencies if venv missing

start-celery-worker.ps1
  - Activates venv automatically
  - Runs: celery -A app.celery_config worker
  - Concurrency: 4 workers
  - Executes tasks scheduled by APScheduler
  - Auto-installs dependencies if venv missing

start-flower.ps1
  - Activates venv automatically
  - Runs: celery -A app.celery_config flower
  - Port: http://localhost:5555
  - Login: admin / admin
  - Monitor all tasks and workers in real-time

start-redis.ps1
  - Uses Docker container (redis-natpudan)
  - Port: localhost:6379
  - Persistent storage: redis-data volume
  - Auto-restart on failure

═══════════════════════════════════════════════════════════════════════════════

HOW TO TEST AUTOMATIC KB UPDATES:

1. Start all 4 terminals (Redis, Backend, Celery, Flower)
2. Open Flower: http://localhost:5555
3. Wait until 2 AM UTC (or trigger manually)
4. Watch Flower for background tasks executing
5. Check backend logs for KB update progress

Manual test (if you want to trigger immediately):
  1. Start all 4 terminals
  2. Open: http://127.0.0.1:8000/docs
  3. POST /api/medical/knowledge/update-knowledge-base
  4. Watch Flower for task execution

═══════════════════════════════════════════════════════════════════════════════

WHAT'S HAPPENING BEHIND THE SCENES:

1. FastAPI (Terminal 2) starts APScheduler
   → Schedules KB update for 2 AM UTC daily

2. When scheduled time arrives:
   → APScheduler submits task to Celery queue
   → Task appears in Redis message broker

3. Celery Worker (Terminal 3) picks up task:
   → Fetches 5 PubMed papers per medical topic
   → Generates OpenAI embeddings
   → Updates FAISS vector database
   → Stores in backend/data/knowledge_base/

4. Flower (Terminal 4) shows:
   → Task status (pending, started, success, failure)
   → Worker availability
   → Execution time
   → Task results

═══════════════════════════════════════════════════════════════════════════════

CONFIGURATION:

Edit backend/kb_update_config.json to customize:
  - Schedule (time, frequency)
  - Medical topics to fetch
  - Papers per topic
  - Time range for papers
  - Max retries and timeout

═══════════════════════════════════════════════════════════════════════════════

All scripts are ready! Just run them in order and enjoy automatic KB updates! 🚀
