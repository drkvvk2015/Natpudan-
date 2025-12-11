# Knowledge Base Auto-Update API Documentation

## Overview
The APScheduler + Celery integration provides automatic knowledge base updates from PubMed and other medical sources. Updates are scheduled daily and execute in the background without blocking the API.

---

## Endpoints

### 1. Manual KB Update (Trigger Anytime)
**POST** `/api/medical/knowledge/pubmed-auto-update`

Manually submit a knowledge base update task to Celery queue.

**Request Body:**
```json
{
  "topics": [
    "diabetes mellitus",
    "hypertension",
    "cancer"
  ],
  "papers_per_topic": 5,
  "days_back": 7
}
```

**Parameters:**
- `topics` (array, optional): Medical topics to search. Default: ["diabetes mellitus", "hypertension", "heart disease", "cancer", "pneumonia", "COVID-19", "depression", "arthritis"]
- `papers_per_topic` (integer, optional): Papers to fetch per topic. Default: 5
- `days_back` (integer, optional): Only include papers from last N days. Default: 7

**Response (Immediate - Task Queued):**
```json
{
  "status": "success",
  "task_id": "abc123def456ghijkl",
  "timestamp": "2025-12-11T14:45:30.123456",
  "result": {
    "topics_searched": 3,
    "papers_found": 15,
    "papers_indexed": 15,
    "errors": [],
    "timestamp": "2025-12-11T14:45:30.123456"
  }
}
```

**Description:**
- Returns immediately after queuing task
- Celery worker executes in background
- API stays responsive during update
- Use task_id to monitor status in Flower

**Example (PowerShell):**
```powershell
$uri = "http://localhost:8000/api/medical/knowledge/pubmed-auto-update"
$body = @{
    topics = @("diabetes", "hypertension", "cancer")
    papers_per_topic = 5
    days_back = 7
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri $uri -Method Post `
    -ContentType "application/json" `
    -Body $body

Write-Host "Task ID: $($response.task_id)"
Write-Host "Papers Found: $($response.result.papers_found)"
Write-Host "Papers Indexed: $($response.result.papers_indexed)"
```

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/api/medical/knowledge/pubmed-auto-update \
  -H "Content-Type: application/json" \
  -d '{
    "topics": ["diabetes", "hypertension"],
    "papers_per_topic": 3,
    "days_back": 7
  }'
```

---

### 2. Fetch Latest Research (Read-Only)
**GET** `/api/medical/knowledge/pubmed-latest`

Fetch latest research papers on a specific topic (doesn't update KB, just reads).

**Query Parameters:**
- `topic` (string, optional): Medical topic. Default: "diabetes"
- `max_results` (integer, optional): Max papers to return. Default: 5
- `days_back` (integer, optional): Only recent papers (N days). Default: 30

**Response:**
```json
{
  "topic": "diabetes",
  "papers": [
    {
      "pubmed_id": "38123456",
      "title": "Novel Insulin Delivery Methods in Type 2 Diabetes",
      "authors": "Smith J, Johnson K, Lee R",
      "publication_date": "2024-12",
      "journal": "Diabetes Care",
      "abstract": "This study evaluated...",
      "url": "https://pubmed.ncbi.nlm.nih.gov/38123456/",
      "fetched_at": "2025-12-11T14:30:00.000000"
    }
  ],
  "count": 5,
  "days_back": 30
}
```

**Example (PowerShell):**
```powershell
$response = Invoke-RestMethod `
    "http://localhost:8000/api/medical/knowledge/pubmed-latest?topic=diabetes&max_results=5"

$response.papers | ForEach-Object {
    Write-Host "Title: $($_.title)"
    Write-Host "Authors: $($_.authors)"
    Write-Host "Journal: $($_.journal)"
    Write-Host "---"
}
```

---

### 3. KB Statistics
**GET** `/api/medical/knowledge/statistics`

View current knowledge base state (documents, topics, indexed date).

**Response:**
```json
{
  "total_documents": 245,
  "indexed_date": "2025-12-11T14:30:00.000000",
  "topics_covered": 8,
  "last_update": "2025-12-11T02:00:00.000000",
  "index_size_mb": 45.2,
  "documents_by_source": {
    "PubMed": 150,
    "PDF Upload": 95
  }
}
```

---

### 4. Task Status (via Celery)
**GET** `/api/tasks/{task_id}`

Check status of a submitted KB update task.

**Response (Running):**
```json
{
  "task_id": "abc123def456ghijkl",
  "status": "STARTED",
  "progress": "Fetching papers (2/3 topics)",
  "current": 2,
  "total": 3
}
```

**Response (Complete):**
```json
{
  "task_id": "abc123def456ghijkl",
  "status": "SUCCESS",
  "result": {
    "topics_searched": 3,
    "papers_found": 15,
    "papers_indexed": 15,
    "errors": []
  }
}
```

**Response (Failed):**
```json
{
  "task_id": "abc123def456ghijkl",
  "status": "FAILURE",
  "error": "Connection timeout fetching from PubMed"
}
```

---

## Scheduled Updates (Automatic)

### Daily Schedule
- **Time:** 2:00 AM UTC (configurable in main.py)
- **Topics:** 8 standard medical conditions (configurable)
- **Papers per topic:** 5 (configurable)
- **Look-back:** 7 days (configurable)

### What Happens
1. **2:00 AM UTC** - APScheduler triggers
2. **< 1 second** - Task submitted to Celery queue
3. **Celery worker picks up** - Starts fetching papers
4. **30-60 seconds** - Downloads and parses papers
5. **60-120 seconds** - Indexes into FAISS vector database
6. **Task complete** - Result stored in Redis

### Monitoring
- **Logs:** Check backend console output
- **Flower Dashboard:** http://localhost:5555
- **Redis:** View task metadata directly
- **Database:** Check `knowledge_documents` table

---

## Error Handling

### Retry Logic
- **Max retries:** 3 (configurable in tasks.py)
- **Retry delay:** Exponential backoff (60s, 120s, 240s)
- **Timeout:** 3600 seconds (1 hour) per task

### Common Errors

**Error: "Connection refused (Errno 111)"**
- **Cause:** Redis not running
- **Fix:** `.\start-redis.ps1`

**Error: "ConnectionError: Failed to connect to broker"**
- **Cause:** Redis connection issue
- **Fix:** Verify Redis is running on correct port

**Error: "ModuleNotFoundError: No module named 'celery'"**
- **Cause:** Dependencies not installed
- **Fix:** `pip install -r requirements.txt`

**Error: "Failed to fetch from PubMed"**
- **Cause:** PubMed API rate limit or network issue
- **Fix:** Auto-retries 3 times, check logs for details

---

## Configuration

### Change Schedule Time
Edit `backend/app/main.py` (~line 110):
```python
scheduler.add_job(
    schedule_kb_update,
    CronTrigger(hour=3, minute=0),  # 3 AM UTC instead of 2 AM
    ...
)
```

### Change Topics
Edit `backend/app/main.py`, in `schedule_kb_update()`:
```python
task = update_knowledge_base.delay(
    topics=[
        "stroke",
        "chronic kidney disease",
        "asthma"
    ],
    ...
)
```

### Change Papers Per Topic
```python
task = update_knowledge_base.delay(
    topics=topics,
    papers_per_topic=10,  # Changed from 5
    days_back=7
)
```

### Change Look-Back Days
```python
task = update_knowledge_base.delay(
    topics=topics,
    papers_per_topic=5,
    days_back=30  # Changed from 7
)
```

### Redis Connection
Set environment variable:
```powershell
$env:REDIS_URL = "redis://custom-host:6379/0"
```

---

## Monitoring & Debugging

### Check Celery Worker Status
```powershell
# In another terminal
python
>>> from app.celery_config import get_celery_app
>>> celery_app = get_celery_app()
>>> celery_app.control.inspect().active()
```

### View Task History
```bash
redis-cli
> KEYS "celery-task-meta-*"
> GET celery-task-meta-<task-id>
```

### Enable Debug Logging
```python
# In tasks.py or celery_config.py
import logging
logging.getLogger('celery').setLevel(logging.DEBUG)
```

### Flower Dashboard
Open http://localhost:5555
- **Active**: Currently running tasks
- **Processed**: Completed tasks
- **Failed**: Failed tasks with error details
- **Workers**: Status of Celery workers

---

## Examples

### Python (Direct Task Submission)
```python
from app.tasks import update_knowledge_base

# Submit task to Celery queue
task = update_knowledge_base.delay(
    topics=["diabetes", "hypertension", "cancer"],
    papers_per_topic=5,
    days_back=7
)

# Get task ID
print(f"Task ID: {task.id}")

# Check status (non-blocking)
print(f"Status: {task.status}")

# Get result when done (blocking)
result = task.get(timeout=300)
print(f"Papers indexed: {result['papers_indexed']}")
```

### JavaScript (Frontend)
```javascript
// Trigger KB update
async function updateKB() {
  const response = await fetch('/api/medical/knowledge/pubmed-auto-update', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      topics: ['diabetes', 'hypertension'],
      papers_per_topic: 5,
      days_back: 7
    })
  });
  
  const data = await response.json();
  console.log(`Task ID: ${data.task_id}`);
  console.log(`Papers indexed: ${data.result.papers_indexed}`);
}

// Call on button click
document.getElementById('updateBtn').onclick = updateKB;
```

### Scheduled Cron Task (External)
```bash
# Add to crontab (Linux/Mac)
0 2 * * * curl -X POST http://localhost:8000/api/medical/knowledge/pubmed-auto-update \
  -H "Content-Type: application/json" \
  -d '{"topics": ["diabetes"], "papers_per_topic": 5}'
```

---

## Performance Notes

### Typical Update Duration
- **Fetch papers:** 10-20 seconds (PubMed API)
- **Parse metadata:** 2-5 seconds
- **Generate embeddings:** 30-60 seconds (OpenAI)
- **Index into FAISS:** 5-10 seconds
- **Total:** ~1-2 minutes

### Resource Usage
- **CPU:** 20-40% (during indexing)
- **Memory:** 500-800 MB (Celery worker)
- **Network:** 5-10 MB (paper downloads)
- **Disk:** 100-500 MB (new FAISS index)

### Optimization Tips
- Lower `papers_per_topic` to speed up
- Increase `days_back` to get more papers
- Run during off-peak hours (currently 2 AM)
- Monitor with Flower dashboard

---

## Troubleshooting Checklist

- ✅ Redis running? `redis-cli ping`
- ✅ FastAPI running? Check port 8000
- ✅ Celery worker running? Check Terminal 3
- ✅ Dependencies installed? `pip install -r requirements.txt`
- ✅ OPENAI_API_KEY set? Required for embeddings
- ✅ Database initialized? Check database file

---

## Support

For issues:
1. Check backend logs (Terminal 2)
2. Check Celery worker logs (Terminal 3)
3. Check Flower dashboard (http://localhost:5555)
4. Review Redis keys: `redis-cli KEYS "*celery*"`
5. Check APScheduler configuration in main.py

Happy auto-updating! 🚀
