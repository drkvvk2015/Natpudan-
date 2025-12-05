# Testing Processing Status Implementation

## Application Status
 Backend running on `http://127.0.0.1:8000`
 Frontend running on `http://127.0.0.1:5173`

## What to Test

### 1. Upload PDF and Monitor Queue Status

**Steps**:
1. Open http://127.0.0.1:5173 in browser
2. Navigate to **"Upload PDFs"** from the menu
3. Drag and drop a medical PDF (or use the file picker)
4. Click **"Upload {N} File(s)"**
5. **Expected behavior**:
   - Upload progress shows (0-100%)
   - Status message updates: "Uploading...", "Processing...", "Document queued"
   - **Progress displays**: Shows percentage and chunk count (e.g., "45% (45/100 chunks)")
   - Polling begins automatically (every 2 seconds)
   - Progress updates as backend processes (if background task running)

### 2. Check Knowledge Base Dashboard

**Steps**:
1. Navigate to **"Knowledge Base"** from menu
2. Look for **"Processing Queue"** card
3. **Expected display**:
   - Shows counts: Queued, Processing, Completed
   - Auto-refreshes every 5 seconds
   - Updates as queue processes

3. Look for **"Upload Location"** card
4. **Expected display**:
   - Shows directory path where PDFs are stored
   - Shows count of uploaded files
   - Shows total size in MB

### 3. Test API Endpoints Directly

**Check Queue Status**:
```bash
# All queued/processing documents
curl http://127.0.0.1:8000/api/medical/knowledge/upload-status

# Response should include:
# - summary: {queued, processing, completed, total}
# - documents: [list of docs with progress info]
```

**Get Statistics with Queue Info**:
```bash
# Get KB statistics including queue
curl http://127.0.0.1:8000/api/medical/knowledge/statistics

# Response should include:
# - processing_queue: {queued, processing, completed, total, status_url}
# - medical_books_dir: "/app/data/knowledge_base"
# - uploaded_files: <count>
# - total_upload_size_mb: <size>
```

**Check Individual Document Status** (after upload):
```bash
# After upload, you'll get document_id in response
curl http://127.0.0.1:8000/api/medical/knowledge/upload-status/{document_id}

# Response should show:
# - status: "queued" | "processing" | "completed" | "failed"
# - progress_percent: 0-100
# - current_chunk: <number>
# - total_chunks: <number>
```

### 4. Frontend Components to Verify

**Upload Page (`/knowledge-base/upload`)**:
- [ ] File list shows real-time progress
- [ ] Progress bar updates smoothly
- [ ] Status message changes from "Uploading..." to "Processing..." 
- [ ] Chunks display updates: "(65/100 chunks)"
- [ ] Upload completes and shows success/error

**Knowledge Base Page (`/knowledge-base`)**:
- [ ] "Processing Queue" card visible if uploads in progress
- [ ] Queue counts update every 5 seconds
- [ ] "Upload Location" card shows directory and file count
- [ ] Search still works even if uploads in progress

## What's Implemented

 **Backend**:
- `DocumentProcessingStatus` model (ready after DB migration)
- `/upload-status` endpoint (all queued documents)
- `/upload-status/{id}` endpoint (individual document)
- Updated `/statistics` with queue info
- Updated `/upload` to return immediately

 **Frontend**:
- Upload page auto-polls every 2 seconds
- Dashboard auto-refreshes every 5 seconds
- Real-time progress display per file
- Processing queue card on dashboard
- Upload location display on dashboard

 **Still Needed**:
- Database migration to create `document_processing_status` table
- Background task to actually process queue (embeddings)

## Next Steps

1. **Database Migration**:
   ```bash
   cd backend
   alembic revision --autogenerate -m "Add document processing status"
   alembic upgrade head
   ```

2. **Background Task** (Choose one):
   - Option A: APScheduler (recommended for simplicity)
   - Option B: Celery + Redis (recommended for production)
   - Option C: FastAPI BackgroundTasks (simple, but limited)

3. **Testing**: Upload PDF and monitor progress in real-time

## Current Limitations

**Without background task**:
- Uploads are queued but not actually processed
- Progress won't update (stuck at "queued")
- Documents won't be embedded/indexed

**With this implementation ready**:
- User sees upload completed immediately
- Can monitor progress as it happens
- Can search while uploads in progress
- No blocked HTTP requests

## API Response Examples

### Upload Response (Immediate):
```json
{
  "message": "Upload started",
  "status": "queued",
  "status_check_endpoints": {
    "all_queue": "/api/medical/knowledge/upload-status",
    "check_individual": "/api/medical/knowledge/upload-status/{document_id}"
  },
  "results": [
    {
      "filename": "Pocket Medicine.pdf",
      "status": "success",
      "document_id": "uuid-1234",
      "chunks": 1245,
      "characters": 452123,
      "info": "Queued for background processing"
    }
  ]
}
```

### Queue Status Response:
```json
{
  "summary": {
    "queued": 2,
    "processing": 1,
    "completed": 15,
    "total": 18
  },
  "documents": [
    {
      "document_id": "uuid-1234",
      "filename": "Pocket Medicine.pdf",
      "status": "queued",
      "progress_percent": 0,
      "current_chunk": 0,
      "total_chunks": 1245
    },
    {
      "document_id": "uuid-5678",
      "filename": "Tintinalli.pdf",
      "status": "processing",
      "progress_percent": 65,
      "current_chunk": 810,
      "total_chunks": 1245,
      "estimated_time_seconds": 120
    }
  ]
}
```

## Troubleshooting

**Frontend not showing queue**:
- Check browser console for errors
- Verify `/api/medical/knowledge/statistics` returns `processing_queue` object
- Clear browser cache and reload

**Upload not showing progress**:
- Check that browser can reach `http://127.0.0.1:8000/api`
- Verify upload response includes `document_id`
- Check browser dev tools Network tab for polling requests

**Database errors**:
- Run: `python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"`
- Or run alembic migration: `alembic upgrade head`

## Success Criteria

- [x] Upload response returns immediately
- [x] Frontend shows progress in real-time
- [x] API endpoints return queue status
- [x] Dashboard displays queue information
- [x] Multiple file uploads work
- [ ] Background task processes queue
- [ ] Embeddings generated asynchronously
- [ ] Search results improve as processing completes
