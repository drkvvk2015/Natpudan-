"""
Background Task Worker for Processing PDF Upload Queue
Monitors DocumentProcessingStatus table and processes queued documents
"""

import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Callable
import time

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import DocumentProcessingStatus, KnowledgeDocument
from app.services.enhanced_knowledge_base import get_knowledge_base
from app.services.pdf_ocr_processor import get_pdf_ocr_processor

logger = logging.getLogger(__name__)

class UploadQueueProcessor:
    """Processes queued PDF uploads in background"""
    
    def __init__(self):
        self.is_running = False
        self.batch_size = 3  # Process 3 at a time
        self.check_interval = 10  # Check queue every 10 seconds
        self.max_retries = 3
        self.max_processing_time = 3600  # 1 hour max per document
        
    def start(self):
        """Start the background worker"""
        if self.is_running:
            logger.warning("[QUEUE] Worker already running")
            return
        
        self.is_running = True
        logger.info("[QUEUE] Starting PDF upload queue processor")
        logger.info(f"[QUEUE] Batch size: {self.batch_size}, Check interval: {self.check_interval}s")
        
    def stop(self):
        """Stop the background worker"""
        self.is_running = False
        logger.info("[QUEUE] Stopping PDF upload queue processor")
    
    def process_queue_sync(self, db: Optional[Session] = None) -> dict:
        """
        Process queued documents synchronously
        Called periodically by the application
        
        Returns:
            {
                'processed': int,
                'failed': int,
                'completed': int,
                'still_queued': int,
                'timestamp': str
            }
        """
        if not self.is_running:
            return {
                'processed': 0,
                'failed': 0,
                'completed': 0,
                'still_queued': 0,
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'worker_not_running'
            }
        
        db_session = db or SessionLocal()
        try:
            # Get queued documents
            queued = db_session.query(DocumentProcessingStatus).filter(
                DocumentProcessingStatus.status == 'queued'
            ).order_by(
                DocumentProcessingStatus.created_at
            ).limit(self.batch_size).all()
            
            if not queued:
                # Get processing stats
                processing = db_session.query(DocumentProcessingStatus).filter(
                    DocumentProcessingStatus.status == 'processing'
                ).count()
                completed = db_session.query(DocumentProcessingStatus).filter(
                    DocumentProcessingStatus.status == 'completed'
                ).count()
                failed = db_session.query(DocumentProcessingStatus).filter(
                    DocumentProcessingStatus.status == 'failed'
                ).count()
                
                return {
                    'processed': 0,
                    'failed': 0,
                    'completed': completed,
                    'still_queued': 0,
                    'processing': processing,
                    'total_failed': failed,
                    'timestamp': datetime.utcnow().isoformat(),
                    'status': 'queue_empty'
                }
            
            processed = 0
            failed = 0
            
            # Process each queued document
            for doc_status in queued:
                try:
                    success = self._process_document(db_session, doc_status)
                    if success:
                        processed += 1
                    else:
                        failed += 1
                except Exception as e:
                    logger.error(f"[QUEUE] Error processing {doc_status.document_id}: {e}")
                    failed += 1
                    # Update with error
                    doc_status.status = 'failed'
                    doc_status.error_message = str(e)[:500]
                    doc_status.completed_at = datetime.utcnow()
                    db_session.commit()
            
            # Get final stats
            still_queued = db_session.query(DocumentProcessingStatus).filter(
                DocumentProcessingStatus.status == 'queued'
            ).count()
            completed = db_session.query(DocumentProcessingStatus).filter(
                DocumentProcessingStatus.status == 'completed'
            ).count()
            
            logger.info(f"[QUEUE] Batch complete: {processed} processed, {failed} failed, {still_queued} still queued")
            
            return {
                'processed': processed,
                'failed': failed,
                'completed': completed,
                'still_queued': still_queued,
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'processed'
            }
            
        except Exception as e:
            logger.error(f"[QUEUE] Error in process_queue_sync: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'processed': 0,
                'failed': 0,
                'completed': 0,
                'still_queued': 0,
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'error',
                'error': str(e)
            }
        finally:
            if db is None:
                db_session.close()
    
    def _process_document(self, db: Session, doc_status: DocumentProcessingStatus) -> bool:
        """
        Process a single document (generate embeddings, etc)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the knowledge document
            kb_doc = db.query(KnowledgeDocument).filter(
                KnowledgeDocument.document_id == doc_status.document_id
            ).first()
            
            if not kb_doc:
                logger.error(f"[PROCESS] Knowledge document not found: {doc_status.document_id}")
                doc_status.status = 'failed'
                doc_status.error_message = "Knowledge document not found"
                doc_status.completed_at = datetime.utcnow()
                db.commit()
                return False
            
            # Update status to processing
            doc_status.status = 'processing'
            doc_status.started_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"[PROCESS] Starting: {kb_doc.filename}")
            
            # Check file exists
            if not Path(kb_doc.file_path).exists():
                raise FileNotFoundError(f"PDF file not found: {kb_doc.file_path}")
            
            # Load canonical text if available (faster and deterministic), fallback to extraction
            canonical_text_path = Path("data/knowledge_base/text") / f"{doc_status.document_id}.txt"
            if canonical_text_path.exists():
                text_content = canonical_text_path.read_text(encoding="utf-8", errors="ignore")
                extraction_method = "canonical_text"
            else:
                # Fallback extraction path
                ocr_processor = get_pdf_ocr_processor()
                pdf_result = ocr_processor.extract_pdf_with_images(
                    Path(kb_doc.file_path),
                    extract_images=True,
                    use_ocr=True,
                    document_id=doc_status.document_id
                )
                text_content = pdf_result['text']
                extraction_method = pdf_result.get("method", "ocr_or_text")

            total_chars = len(text_content or "")
            if not text_content.strip():
                raise ValueError("No text content available for embedding")

            # Add to vector KB (real processing, not simulated)
            knowledge_base = get_knowledge_base()
            total_chunks = max(1, kb_doc.chunk_count or 1)

            # Progress: extraction/prep complete
            doc_status.current_chunk = 0
            doc_status.progress_percent = 10
            doc_status.estimated_time_seconds = max(5, int(total_chunks * 0.6))
            db.commit()

            added_chunks = knowledge_base.add_document(
                content=text_content,
                metadata={
                    "source": kb_doc.filename,
                    "filename": kb_doc.filename,
                    "document_id": doc_status.document_id,
                    "category": kb_doc.category or "medical_pdf",
                    "section": "body",
                    "indexed_at": datetime.utcnow().isoformat(),
                    "processing_type": doc_status.processing_type or "embedding",
                    "extraction_method": extraction_method,
                },
                chunk_size=2000,
                chunk_overlap=50
            )

            # Progress complete
            doc_status.current_chunk = max(1, int(added_chunks or total_chunks))
            doc_status.total_chunks = max(1, int(added_chunks or total_chunks))
            doc_status.progress_percent = 100
            doc_status.status = 'completed'
            doc_status.completed_at = datetime.utcnow()
            doc_status.estimated_time_seconds = 0

            # Update knowledge document
            kb_doc.is_indexed = True
            kb_doc.indexed_at = datetime.utcnow()
            if added_chunks:
                kb_doc.chunk_count = int(added_chunks)

            db.commit()

            logger.info(
                f"[PROCESS] Completed: {kb_doc.filename} ({total_chars} chars, {kb_doc.chunk_count} chunks, method={extraction_method})"
            )
            return True
            
        except Exception as e:
            logger.error(f"[PROCESS] Error processing document: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            doc_status.status = 'failed'
            doc_status.error_message = str(e)[:500]
            doc_status.completed_at = datetime.utcnow()
            
            # Increment retry count
            if doc_status.retry_count is None:
                doc_status.retry_count = 0
            doc_status.retry_count += 1
            
            # If retries exceeded, mark as failed
            if doc_status.retry_count >= self.max_retries:
                logger.warning(f"[PROCESS] Max retries exceeded for {doc_status.document_id}")
                doc_status.status = 'failed'
            else:
                # Reset to queued for retry
                doc_status.status = 'queued'
                logger.info(f"[PROCESS] Queuing for retry ({doc_status.retry_count}/{self.max_retries})")
            
            db.commit()
            return False


# Singleton instance
_processor = None

def get_queue_processor() -> UploadQueueProcessor:
    """Get singleton queue processor instance"""
    global _processor
    if _processor is None:
        _processor = UploadQueueProcessor()
    return _processor


def process_upload_queue() -> dict:
    """
    Process the upload queue (called periodically)
    Entry point for background task runners
    """
    processor = get_queue_processor()
    return processor.process_queue_sync()
