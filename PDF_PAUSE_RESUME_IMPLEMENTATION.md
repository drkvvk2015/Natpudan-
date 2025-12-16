# PDF Processing with Pause/Resume Implementation Guide

## Overview
This document describes the complete implementation of PDF processing with pause/resume capability for the Natpudan AI Medical Assistant knowledge base.

## Architecture

### Components

#### 1. Database Model (backend/app/models.py)
**PDFProcessingStatus Enum:**
- `PENDING` - Waiting to start processing
- `PROCESSING` - Currently processing
- `PAUSED` - Paused by user
- `COMPLETED` - Successfully completed
- `FAILED` - Processing failed

**PDFProcessing Model:**
- `id` - Primary key
- `pdf_file_id` - Foreign key to PDFFile
- `pdf_name` - Original PDF filename
- `status` - Current processing status (PDFProcessingStatus enum)
- `total_pages` - Total pages in PDF
- `pages_processed` - Pages completed so far
- `last_page_processed` - Page number to resume from (checkpoint)
- `embeddings_created` - Count of embeddings generated
- `error_message` - Human-readable error message
- `error_details` - JSON with detailed error info
- `file_size` - Size of PDF in bytes
- `started_at` - When processing started
- `paused_at` - When processing was paused
- `completed_at` - When processing completed
- `user_id` - User who initiated processing
- `retry_count` - Number of retry attempts
- `progress_percentage` - Calculated property (0-100%)

**User Relationship:**
```python
pdf_processing_jobs = relationship(
    "PDFProcessing",
    back_populates="user",
    cascade="all, delete-orphan"
)
```

#### 2. Processing Manager Service (backend/app/services/pdf_processing_manager.py)

**PDFProcessingState Class:**
- Manages pause/resume events for each processing task
- Uses `asyncio.Event` objects for signaling
- Methods:
  - `create_task()` - Initialize new task state
  - `pause_task()` - Pause processing
  - `resume_task()` - Resume processing
  - `stop_task()` - Stop processing
  - `cleanup_task()` - Clean up state
  - `wait_if_paused()` - Async wait when paused
  - `should_stop()` - Check if stop requested

**PDFProcessorWithPauseResume Class:**
- Main processor for PDF files with checkpoint support
- Uses PyPDF2 for text extraction
- Creates embeddings via VectorKnowledgeBase
- Methods:
  - `process_pdf_with_checkpoint()` - Main async processing loop
  - `_process_page()` - Process single page and create embeddings
  - `pause_processing()` - Pause active processing
  - `resume_processing()` - Resume paused processing
  - `cancel_processing()` - Cancel and mark failed
  - `get_processing_status()` - Get current status dict

**Key Features:**
- **Checkpoint System**: Saves `last_page_processed` after each page
- **Pause/Resume**: Uses asyncio.Event for cooperative pausing
- **Error Handling**: Detailed error tracking with rollback capability
- **Progress Tracking**: Real-time page/embeddings count

#### 3. API Endpoints (backend/app/api/knowledge_base.py)

**POST /api/knowledge-base/pdf/pause/{processing_id}**
- Pause an active PDF processing job
- Returns: `{status: "paused", processing_id: int}`
- Auth: Requires doctor/admin role

**POST /api/knowledge-base/pdf/resume/{processing_id}**
- Resume a paused PDF processing job
- Starts background task to continue processing
- Returns: `{status: "resumed", processing_id: int}`
- Auth: Requires doctor/admin role

**GET /api/knowledge-base/pdf/status/{processing_id}**
- Get current status of processing job
- Returns:
  ```json
  {
    "success": true,
    "data": {
      "id": 1,
      "pdf_name": "medical_handbook.pdf",
      "status": "PROCESSING",
      "progress_percentage": 45,
      "pages_processed": 90,
      "total_pages": 200,
      "embeddings_created": 450,
      "error_message": null
    }
  }
  ```
- Auth: Requires doctor/admin role

**POST /api/knowledge-base/pdf/cancel/{processing_id}**
- Cancel a processing job
- Returns: `{status: "cancelled", processing_id: int}`
- Auth: Requires doctor/admin role

**GET /api/knowledge-base/pdf/processing-list**
- Get all processing jobs for current user
- Returns:
  ```json
  {
    "success": true,
    "total": 5,
    "data": [
      {
        "id": 1,
        "pdf_name": "file.pdf",
        "status": "PROCESSING",
        "progress_percentage": 45,
        ...
      }
    ]
  }
  ```
- Auth: Requires doctor/admin role

#### 4. Background Task Handler (backend/app/services/pdf_task_handler.py)

**PDFProcessingTaskHandler Class:**
- Manages background PDF processing tasks
- Integrates with FastAPI BackgroundTasks
- Methods:
  - `process_pdf_task()` - Process single PDF
  - `process_batch_pdfs()` - Process multiple PDFs sequentially
  - `retry_failed_processing()` - Retry failed jobs
  - `cleanup_stale_processing()` - Clean up abandoned jobs

**Functions:**
- `process_pdf_background()` - Async wrapper for single processing
- `process_batch_pdfs_background()` - Async wrapper for batch processing

#### 5. Frontend Component (frontend/src/components/PDFProcessingStatus.tsx)

**PDFProcessingStatus React Component:**
- Real-time status display with auto-refresh (2sec default)
- Features:
  - Progress bars for each job
  - Pause/Resume/Cancel buttons
  - Error message display
  - Timestamp tracking
  - Status badges with color coding

**Props:**
- `refreshInterval?: number` - Poll interval in ms (default: 2000)
- `autoRefresh?: boolean` - Enable auto-refresh (default: true)

**Usage:**
```tsx
import PDFProcessingStatus from './components/PDFProcessingStatus';

function KnowledgeBaseManager() {
  return (
    <PDFProcessingStatus 
      refreshInterval={2000}
      autoRefresh={true}
    />
  );
}
```

## Workflow

### Starting PDF Processing

1. User uploads PDF via existing knowledge base upload endpoint
2. System creates `PDFProcessing` record with status=`PENDING`
3. FastAPI BackgroundTasks starts `process_pdf_background()`
4. PDFProcessorWithPauseResume begins processing

### During Processing

1. Processor reads PDF page by page
2. For each page:
   - Check pause event: `await wait_if_paused()`
   - Check stop event: `should_stop()`
   - Extract text and create embeddings
   - Save `last_page_processed` checkpoint
   - Update `pages_processed` count
3. Frontend polls `/api/knowledge-base/pdf/status/{id}` every 2 seconds
4. Progress bar updates in real-time

### Pausing Processing

1. User clicks "Pause" button in frontend
2. Frontend calls POST `/api/knowledge-base/pdf/pause/{processing_id}`
3. Backend clears pause event (blocking processing loop)
4. Processing pauses at next checkpoint
5. Database saves `paused_at` timestamp and `last_page_processed`

### Resuming Processing

1. User clicks "Resume" button
2. Frontend calls POST `/api/knowledge-base/pdf/resume/{processing_id}`
3. Backend sets pause event (unblocking processing loop)
4. BackgroundTasks starts new task from `last_page_processed`
5. Processing continues from checkpoint

### Cancellation

1. User clicks "Cancel" button
2. Frontend calls POST `/api/knowledge-base/pdf/cancel/{processing_id}`
3. Backend sets stop event
4. Processing stops, marked as `FAILED`
5. Error message: "Processing cancelled by user"

## Implementation Checklist

- [x] Database models: PDFProcessingStatus, PDFProcessing
- [x] User relationship to pdf_processing_jobs
- [x] PDFProcessingState class with asyncio.Event
- [x] PDFProcessorWithPauseResume service
- [x] Checkpoint-based page processing
- [x] API endpoints (pause, resume, status, cancel, list)
- [x] PDFProcessingStatus React component
- [x] Background task handler
- [ ] Database migration (Alembic)
- [ ] Integration with existing PDF upload endpoint
- [ ] Testing suite
- [ ] Celery integration (optional, for production)

## Database Migration

When ready to deploy, run Alembic migration:

```bash
# Generate migration
alembic revision --autogenerate -m "Add PDF processing pause/resume support"

# Apply migration
alembic upgrade head
```

## Configuration

### Backend Settings

Add to `.env`:
```
# PDF Processing
PDF_PROCESSING_BATCH_SIZE=5  # Concurrent batch processing limit
PDF_PROCESSING_TIMEOUT=3600  # Timeout in seconds
PDF_EMBEDDING_CACHE_SIZE=1000  # Embeddings cache size
```

### Frontend Settings

Configure in `PDFProcessingStatus` component:
```tsx
<PDFProcessingStatus 
  refreshInterval={2000}  // Adjust for different polling speeds
  autoRefresh={true}      // Set false for manual refresh only
/>
```

## Error Handling

### Common Errors

**PDF Not Found:**
- Status: 404
- Message: "PDF file not found"
- Action: Verify file path exists

**Permission Denied:**
- Status: 403
- Message: "Access denied. Knowledge Base management requires Admin or Doctor role"
- Action: Ensure user has proper role

**Processing Not Found:**
- Status: 404
- Message: "Processing job {id} not found"
- Action: Check processing_id is correct

**Invalid Status Transition:**
- Status: 400
- Message: "Cannot pause processing in status: COMPLETED"
- Action: Only pause PROCESSING jobs

**Timeout:**
- Status: 500 (internal)
- Message: "Timeout after 24 hours"
- Action: `cleanup_stale_processing()` marks as failed

### Retry Logic

Failed jobs can be retried up to `max_retries` times:
```python
results = await pdf_task_handler.retry_failed_processing(max_retries=3)
```

## Performance Considerations

1. **Checkpoint Frequency**: Save state after each page
   - Trade-off: Database writes vs resumption granularity
   - Currently: Per-page (most granular)

2. **Batch Processing**: Process PDFs sequentially
   - Prevents resource exhaustion
   - Adjust `PDF_PROCESSING_BATCH_SIZE` for parallelism

3. **Embedding Caching**: Reuse embeddings for duplicate content
   - VectorKnowledgeBase handles caching
   - Check FAISS index size regularly

4. **Database Queries**: Use indices on (user_id, status, created_at)
   - Improves list and filtering queries

## Testing

### Manual Testing

1. **Start Processing:**
   ```bash
   POST /api/knowledge-base/pdf/upload
   # Returns: {processing_id: 1, pdf_name: "test.pdf"}
   ```

2. **Pause Processing:**
   ```bash
   POST /api/knowledge-base/pdf/pause/1
   # Returns: {status: "paused"}
   ```

3. **Check Status:**
   ```bash
   GET /api/knowledge-base/pdf/status/1
   # Returns: {progress_percentage: 45, ...}
   ```

4. **Resume Processing:**
   ```bash
   POST /api/knowledge-base/pdf/resume/1
   # Returns: {status: "resumed"}
   ```

5. **Cancel Processing:**
   ```bash
   POST /api/knowledge-base/pdf/cancel/1
   # Returns: {status: "cancelled"}
   ```

### Unit Tests

Create `backend/tests/test_pdf_processing.py`:
```python
import pytest
from app.services.pdf_processing_manager import PDFProcessingState

def test_pause_resume():
    state = PDFProcessingState()
    state.create_task(1)
    state.pause_task(1)
    assert not state.pause_events[1].is_set()
    state.resume_task(1)
    assert state.pause_events[1].is_set()
```

## Production Deployment

### Celery Integration (Optional)

For production multi-worker setup:

```python
# In main.py
from celery import Celery

celery_app = Celery(
    "natpudan",
    broker="redis://localhost:6379",
    backend="redis://localhost:6379"
)

@celery_app.task
def process_pdf_task(processing_id: int):
    return asyncio.run(pdf_task_handler.process_pdf_task(processing_id))
```

### Monitoring

1. **Track Job Status**: Use database queries
   ```python
   completed = db.query(PDFProcessing).filter(
       PDFProcessing.status == PDFProcessingStatus.COMPLETED
   ).count()
   ```

2. **Alert on Failures**: Monitor error_message field
   ```python
   failed = db.query(PDFProcessing).filter(
       PDFProcessing.status == PDFProcessingStatus.FAILED
   ).all()
   ```

3. **Resource Monitoring**: Track embeddings_created count
   ```python
   total_embeddings = db.query(func.sum(PDFProcessing.embeddings_created)).scalar()
   ```

## Future Enhancements

1. **Parallel Page Processing**: Process multiple pages concurrently
2. **Batch API**: Upload and process multiple PDFs at once
3. **WebSocket Real-time Updates**: Instead of polling
4. **Compression**: Store compressed embeddings
5. **Archive Processing**: Move completed jobs to archive
6. **Analytics**: Track processing times, success rates
7. **Notifications**: Email alerts when processing completes/fails
8. **Rate Limiting**: Limit processing resources per user

## Troubleshooting

### Processing Stuck in PROCESSING Status

```python
# Manually cleanup
from app.services.pdf_task_handler import pdf_task_handler
results = await pdf_task_handler.cleanup_stale_processing(timeout_hours=1)
```

### High Database Query Load

- Add index: `CREATE INDEX idx_pdf_processing_user_status ON pdf_processing(user_id, status)`
- Archive old completed jobs

### Out of Memory

- Reduce PDF batch size
- Increase checkpoint frequency
- Enable garbage collection between pages

### Embedding Generation Slow

- Check VectorKnowledgeBase caching
- Reduce chunk size
- Verify OpenAI API quota
- Consider bulk embedding API

## Support

For issues or questions:
1. Check logs: `backend/logs/pdf_processing.log`
2. Review database: `SELECT * FROM pdf_processing WHERE status = 'FAILED'`
3. Test endpoints with Postman collection
4. Review implementation in respective files
