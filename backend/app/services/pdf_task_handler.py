"""Background task handlers for PDF processing."""

import asyncio
import logging
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models import Base, PDFProcessing, PDFFile, PDFProcessingStatus
from backend.app.services.pdf_processing_manager import pdf_processor_with_resume
from backend.app.database import DATABASE_URL

logger = logging.getLogger(__name__)


class PDFProcessingTaskHandler:
    """Handles background PDF processing tasks."""
    
    def __init__(self, db_url: str = DATABASE_URL):
        """Initialize task handler with database connection."""
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_db_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    async def process_pdf_task(self, processing_id: int) -> bool:
        """
        Background task to process a PDF with pause/resume support.
        
        Args:
            processing_id: ID of PDFProcessing record
        
        Returns:
            True if successful, False otherwise
        """
        db = self.get_db_session()
        try:
            # Get processing record
            processing = db.query(PDFProcessing).filter(
                PDFProcessing.id == processing_id
            ).first()
            
            if not processing:
                logger.error(f"Processing record {processing_id} not found")
                return False
            
            # Get PDF file
            pdf_file = db.query(PDFFile).filter(
                PDFFile.id == processing.pdf_file_id
            ).first()
            
            if not pdf_file:
                logger.error(f"PDF file not found for processing {processing_id}")
                processing.status = PDFProcessingStatus.FAILED
                processing.error_message = "PDF file not found"
                db.commit()
                return False
            
            logger.info(f"Starting PDF processing task {processing_id}: {pdf_file.file_path}")
            
            # Process PDF with checkpoint support
            result = await pdf_processor_with_resume.process_pdf_with_checkpoint(
                processing_id,
                pdf_file.file_path,
                db,
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in PDF processing task {processing_id}: {str(e)}")
            try:
                processing = db.query(PDFProcessing).filter(
                    PDFProcessing.id == processing_id
                ).first()
                if processing:
                    processing.status = PDFProcessingStatus.FAILED
                    processing.error_message = f"Task error: {str(e)}"
                    db.commit()
            except Exception as db_error:
                logger.error(f"Failed to update error status: {str(db_error)}")
            
            return False
        
        finally:
            db.close()
    
    async def process_batch_pdfs(self, processing_ids: list[int]) -> dict:
        """
        Process multiple PDFs sequentially with pause/resume support.
        
        Args:
            processing_ids: List of PDFProcessing IDs
        
        Returns:
            Dictionary with results
        """
        results = {
            "total": len(processing_ids),
            "completed": 0,
            "failed": 0,
            "details": []
        }
        
        for processing_id in processing_ids:
            try:
                success = await self.process_pdf_task(processing_id)
                if success:
                    results["completed"] += 1
                    results["details"].append({
                        "processing_id": processing_id,
                        "status": "completed"
                    })
                else:
                    results["failed"] += 1
                    results["details"].append({
                        "processing_id": processing_id,
                        "status": "failed"
                    })
            except Exception as e:
                logger.error(f"Error processing batch item {processing_id}: {str(e)}")
                results["failed"] += 1
                results["details"].append({
                    "processing_id": processing_id,
                    "status": "error",
                    "error": str(e)
                })
        
        logger.info(f"Batch processing completed: {results['completed']}/{results['total']} successful")
        return results
    
    async def retry_failed_processing(self, max_retries: int = 3) -> dict:
        """
        Retry failed PDF processing jobs.
        
        Args:
            max_retries: Maximum retry attempts
        
        Returns:
            Dictionary with retry results
        """
        db = self.get_db_session()
        try:
            # Find failed processing jobs that haven't exceeded retry limit
            failed_jobs = db.query(PDFProcessing).filter(
                PDFProcessing.status == PDFProcessingStatus.FAILED,
                PDFProcessing.retry_count < max_retries,
            ).all()
            
            results = {
                "total": len(failed_jobs),
                "retried": 0,
                "still_failed": 0,
            }
            
            for job in failed_jobs:
                job.retry_count = (job.retry_count or 0) + 1
                job.status = PDFProcessingStatus.PENDING
                job.last_page_processed = 0  # Reset to restart from beginning
                db.commit()
                
                success = await self.process_pdf_task(job.id)
                if success:
                    results["retried"] += 1
                else:
                    results["still_failed"] += 1
            
            logger.info(f"Retry processing completed: {results['retried']} retried")
            return results
            
        except Exception as e:
            logger.error(f"Error in retry processing: {str(e)}")
            return {
                "error": str(e),
                "total": 0,
                "retried": 0,
                "still_failed": 0,
            }
        finally:
            db.close()
    
    async def cleanup_stale_processing(self, timeout_hours: int = 24) -> dict:
        """
        Clean up stale processing jobs that haven't completed.
        
        Args:
            timeout_hours: Jobs older than this are considered stale
        
        Returns:
            Dictionary with cleanup results
        """
        from datetime import datetime, timedelta
        
        db = self.get_db_session()
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=timeout_hours)
            
            stale_jobs = db.query(PDFProcessing).filter(
                PDFProcessing.status.in_([
                    PDFProcessingStatus.PENDING,
                    PDFProcessingStatus.PROCESSING,
                ]),
                PDFProcessing.started_at < cutoff_time if PDFProcessing.started_at else True,
            ).all()
            
            results = {
                "total": len(stale_jobs),
                "cleaned": 0,
            }
            
            for job in stale_jobs:
                job.status = PDFProcessingStatus.FAILED
                job.error_message = f"Timeout after {timeout_hours} hours"
                db.commit()
                results["cleaned"] += 1
            
            logger.info(f"Cleanup completed: {results['cleaned']} stale jobs cleaned")
            return results
            
        except Exception as e:
            logger.error(f"Error in cleanup: {str(e)}")
            return {
                "error": str(e),
                "total": 0,
                "cleaned": 0,
            }
        finally:
            db.close()


# Global task handler instance
pdf_task_handler = PDFProcessingTaskHandler()


async def process_pdf_background(processing_id: int) -> bool:
    """Simple async wrapper for FastAPI BackgroundTasks."""
    return await pdf_task_handler.process_pdf_task(processing_id)


async def process_batch_pdfs_background(processing_ids: list[int]) -> dict:
    """Simple async wrapper for batch processing."""
    return await pdf_task_handler.process_batch_pdfs(processing_ids)
