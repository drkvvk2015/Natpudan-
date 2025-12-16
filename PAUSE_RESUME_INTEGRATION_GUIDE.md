"""Integration guide for PDF pause/resume with existing upload workflow."""

# This file shows how to integrate the PDF pause/resume feature
# with the existing PDF upload endpoints in knowledge_base.py

# ============================================================================
# INTEGRATION STEP 1: Import the new services and models
# ============================================================================
# Add these imports to backend/app/api/knowledge_base.py at the top:

from app.models import PDFProcessing, PDFProcessingStatus, PDFFile
from app.services.pdf_processing_manager import pdf_processor_with_resume
from app.services.pdf_task_handler import pdf_task_handler


# ============================================================================
# INTEGRATION STEP 2: Modify existing PDF upload endpoint
# ============================================================================
# In the existing upload_pdf or batch_upload_pdfs endpoint, add this
# code after creating/storing the PDF file:

async def create_processing_record_and_start_task(
    pdf_file_id: int,
    pdf_name: str,
    user_id: int,
    db: Session,
    background_tasks: BackgroundTasks,
):
    """
    Create PDFProcessing record and start background task.
    
    Call this after successfully uploading and storing a PDF file.
    """
    try:
        # Create processing record
        processing = PDFProcessing(
            pdf_file_id=pdf_file_id,
            pdf_name=pdf_name,
            status=PDFProcessingStatus.PENDING,
            user_id=user_id,
            total_pages=0,
            pages_processed=0,
            last_page_processed=0,
            embeddings_created=0,
            retry_count=0,
        )
        db.add(processing)
        db.commit()
        db.refresh(processing)
        
        # Get PDF file path
        pdf_file = db.query(PDFFile).filter(PDFFile.id == pdf_file_id).first()
        if not pdf_file:
            raise ValueError(f"PDF file {pdf_file_id} not found")
        
        # Start background processing task
        background_tasks.add_task(
            pdf_processor_with_resume.process_pdf_with_checkpoint,
            processing.id,
            pdf_file.file_path,
            db,
        )
        
        logger.info(
            f"Created processing record {processing.id} for {pdf_name} "
            f"(user: {user_id}, file: {pdf_file_id})"
        )
        
        return {
            "processing_id": processing.id,
            "pdf_name": pdf_name,
            "status": "queued",
            "message": "PDF processing started. Use processing_id to track progress."
        }
    
    except Exception as e:
        logger.error(f"Error creating processing record: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create processing record: {str(e)}"
        )


# ============================================================================
# INTEGRATION STEP 3: Example - Modify existing upload_pdf endpoint
# ============================================================================
# Here's how to modify an existing upload_pdf endpoint:

# BEFORE:
# @router.post("/upload")
# async def upload_pdf(
#     file: UploadFile = File(...),
#     current_user: User = Depends(require_kb_management_role),
#     db: Session = Depends(get_db),
# ):
#     # ... existing upload logic ...
#     # Create PDFFile record
#     pdf_file = PDFFile(file_path=stored_path, ...)
#     db.add(pdf_file)
#     db.commit()
#     return {"status": "success"}

# AFTER:
# @router.post("/upload")
# async def upload_pdf(
#     file: UploadFile = File(...),
#     current_user: User = Depends(require_kb_management_role),
#     db: Session = Depends(get_db),
#     background_tasks: BackgroundTasks = BackgroundTasks(),
# ):
#     # ... existing upload logic ...
#     # Create PDFFile record
#     pdf_file = PDFFile(file_path=stored_path, ...)
#     db.add(pdf_file)
#     db.commit()
#     db.refresh(pdf_file)
#     
#     # NEW: Create processing record and start task
#     result = await create_processing_record_and_start_task(
#         pdf_file.id,
#         file.filename,
#         current_user.id,
#         db,
#         background_tasks,
#     )
#     return result


# ============================================================================
# INTEGRATION STEP 4: Database Migration Command
# ============================================================================
# Run this command to create the PDFProcessing table:

"""
cd backend
alembic revision --autogenerate -m "Add PDF processing pause/resume support"
alembic upgrade head
"""

# Or manually create the table (if not using Alembic):
"""
CREATE TABLE pdf_processing (
    id SERIAL PRIMARY KEY,
    pdf_file_id INTEGER NOT NULL REFERENCES pdf_file(id),
    pdf_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    total_pages INTEGER DEFAULT 0,
    pages_processed INTEGER DEFAULT 0,
    last_page_processed INTEGER DEFAULT 0,
    embeddings_created INTEGER DEFAULT 0,
    error_message TEXT,
    error_details JSON,
    file_size BIGINT,
    started_at TIMESTAMP,
    paused_at TIMESTAMP,
    completed_at TIMESTAMP,
    user_id INTEGER NOT NULL REFERENCES user(id),
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pdf_file_id) REFERENCES pdf_file(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX idx_pdf_processing_user_id ON pdf_processing(user_id);
CREATE INDEX idx_pdf_processing_status ON pdf_processing(status);
CREATE INDEX idx_pdf_processing_user_status ON pdf_processing(user_id, status);
"""


# ============================================================================
# INTEGRATION STEP 5: Frontend Integration
# ============================================================================
# In your knowledge base management page (e.g., frontend/src/pages/KnowledgeBase.tsx):

"""
import PDFProcessingStatus from '../components/PDFProcessingStatus';

export function KnowledgeBasePage() {
  return (
    <div className="space-y-6">
      <div>
        <h2>Upload PDF</h2>
        {/* Existing upload form */}
      </div>
      
      <div className="border-t pt-6">
        <h2>Processing Status</h2>
        <PDFProcessingStatus 
          refreshInterval={2000}
          autoRefresh={true}
        />
      </div>
    </div>
  );
}
"""


# ============================================================================
# INTEGRATION STEP 6: Testing the Integration
# ============================================================================
# Test script to verify the integration works:

"""
# 1. Start backend:
python -m uvicorn app.main:app --reload --port 8000

# 2. Upload a PDF:
curl -X POST http://localhost:8000/api/knowledge-base/upload \\
  -H "Authorization: Bearer <token>" \\
  -F "file=@test.pdf"

# Response should include processing_id
# {
#   "processing_id": 1,
#   "pdf_name": "test.pdf",
#   "status": "queued"
# }

# 3. Check processing status:
curl http://localhost:8000/api/knowledge-base/pdf/status/1 \\
  -H "Authorization: Bearer <token>"

# 4. Pause processing:
curl -X POST http://localhost:8000/api/knowledge-base/pdf/pause/1 \\
  -H "Authorization: Bearer <token>"

# 5. Resume processing:
curl -X POST http://localhost:8000/api/knowledge-base/pdf/resume/1 \\
  -H "Authorization: Bearer <token>"

# 6. Cancel processing:
curl -X POST http://localhost:8000/api/knowledge-base/pdf/cancel/1 \\
  -H "Authorization: Bearer <token>"

# 7. List all processing jobs:
curl http://localhost:8000/api/knowledge-base/pdf/processing-list \\
  -H "Authorization: Bearer <token>"
"""


# ============================================================================
# INTEGRATION STEP 7: Configuration (.env)
# ============================================================================
# Add these settings to backend/.env:

"""
# PDF Processing Settings
PDF_PROCESSING_BATCH_SIZE=5
PDF_PROCESSING_TIMEOUT=3600
PDF_EMBEDDING_CACHE_SIZE=1000
PDF_PROCESSING_LOG_LEVEL=INFO

# Optional: Celery Configuration (for production)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_TASK_TIMEOUT=3600
"""


# ============================================================================
# INTEGRATION STEP 8: Error Handling
# ============================================================================
# The system automatically handles:
# - Stale processing jobs (cleanup_stale_processing)
# - Failed retries (retry_failed_processing)
# - Database session management
# - Async/await coordination

# To manually clean up:
"""
from app.services.pdf_task_handler import pdf_task_handler
import asyncio

# Cleanup stale jobs
results = asyncio.run(pdf_task_handler.cleanup_stale_processing(timeout_hours=24))
print(results)  # {cleaned: 5, total: 5}

# Retry failed jobs
results = asyncio.run(pdf_task_handler.retry_failed_processing(max_retries=3))
print(results)  # {retried: 3, still_failed: 0, total: 3}
"""


# ============================================================================
# FILES CREATED/MODIFIED
# ============================================================================
# New files:
# - backend/app/services/pdf_processing_manager.py (PDFProcessingState, PDFProcessorWithPauseResume)
# - backend/app/services/pdf_task_handler.py (PDFProcessingTaskHandler)
# - frontend/src/components/PDFProcessingStatus.tsx (React component)
# - PDF_PAUSE_RESUME_IMPLEMENTATION.md (This documentation)

# Modified files:
# - backend/app/models.py (Added PDFProcessingStatus enum, PDFProcessing model, User relationship)
# - backend/app/api/knowledge_base.py (Added 5 new endpoints for pause/resume/status)

# Next steps:
# 1. Review models.py to verify PDFProcessing table schema
# 2. Run database migration with Alembic or manual SQL
# 3. Modify existing upload endpoints to call create_processing_record_and_start_task()
# 4. Add PDFProcessingStatus component to knowledge base UI
# 5. Test end-to-end workflow
# 6. (Optional) Set up Celery for production deployment
