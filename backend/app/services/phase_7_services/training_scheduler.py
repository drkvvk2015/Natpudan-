"""
Phase 7: Training Job Scheduler

Manages ML training jobs with queuing, progress tracking, and error handling.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, List
import json
from sqlalchemy.orm import Session
from sqlalchemy import and_
import uuid

from ...database.models import (
    TrainingJob,
    TrainingJobStatus,
    ModelType,
    ValidatedCase,
    ValidationStatus
)

logger = logging.getLogger(__name__)


class TrainingScheduler:
    """
    Manages training job scheduling and execution
    
    Features:
    - Queue management
    - Progress tracking
    - Status transitions
    - Error handling and retry logic
    - Dataset preparation
    """
    
    def __init__(self, db: Session):
        self.db = db
        
    def create_training_job(
        self,
        model_type: ModelType,
        model_version: str,
        dataset_config: Optional[Dict] = None
    ) -> TrainingJob:
        """
        Create a new training job
        
        Args:
            model_type: Type of model to train
            model_version: Version identifier for the model
            dataset_config: Optional configuration for dataset preparation
            
        Returns:
            Created TrainingJob
        """
        try:
            # Generate unique job ID
            job_id = f"TRAIN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
            
            # Count available training data
            dataset_size = self.db.query(ValidatedCase).filter(
                ValidatedCase.validation_status == ValidationStatus.VALIDATED.value,
                ValidatedCase.is_anonymized == True
            ).count()
            
            job = TrainingJob(
                job_id=job_id,
                model_type=model_type.value,
                model_version=model_version,
                status=TrainingJobStatus.QUEUED.value,
                progress_percentage=0,
                dataset_size=dataset_size,
                # Store dataset configuration in hyperparameters JSON
                hyperparameters=json.dumps(dataset_config or {}),
                created_at=datetime.utcnow()
            )
            
            self.db.add(job)
            self.db.commit()
            self.db.refresh(job)
            
            logger.info(f"Created training job {job_id} for {model_type.value}")
            return job
            
        except Exception as e:
            logger.error(f"Error creating training job: {e}")
            self.db.rollback()
            raise
    
    def start_job(self, job_id: str) -> TrainingJob:
        """
        Start a queued training job
        
        Args:
            job_id: ID of the job to start
            
        Returns:
            Updated TrainingJob
        """
        try:
            job = self.db.query(TrainingJob).filter(
                TrainingJob.job_id == job_id
            ).first()
            
            if not job:
                raise ValueError(f"Training job {job_id} not found")
            
            if job.status != TrainingJobStatus.QUEUED.value:
                raise ValueError(f"Job {job_id} is not queued (current: {job.status})")
            
            job.status = TrainingJobStatus.RUNNING.value
            job.start_time = datetime.utcnow()
            job.progress_percentage = 5
            
            self.db.commit()
            self.db.refresh(job)
            
            logger.info(f"Started training job {job_id}")
            return job
            
        except Exception as e:
            logger.error(f"Error starting job {job_id}: {e}")
            self.db.rollback()
            raise
    
    def update_progress(
        self,
        job_id: str,
        progress_percentage: int,
        message: Optional[str] = None
    ) -> TrainingJob:
        """
        Update job progress
        
        Args:
            job_id: ID of the job
            progress_percentage: Progress percentage (0-100)
            message: Optional status message
            
        Returns:
            Updated TrainingJob
        """
        try:
            job = self.db.query(TrainingJob).filter(
                TrainingJob.job_id == job_id
            ).first()
            
            if not job:
                raise ValueError(f"Training job {job_id} not found")
            
            job.progress_percentage = min(max(progress_percentage, 0), 100)
            
            if message:
                current_log = job.training_log or ""
                job.training_log = f"{current_log}\n[{datetime.utcnow()}] {message}"
            
            self.db.commit()
            self.db.refresh(job)
            
            return job
            
        except Exception as e:
            logger.error(f"Error updating progress for {job_id}: {e}")
            self.db.rollback()
            raise
    
    def complete_job(
        self,
        job_id: str,
        final_accuracy: Optional[int] = None,
        metrics: Optional[Dict] = None
    ) -> TrainingJob:
        """
        Mark job as completed
        
        Args:
            job_id: ID of the job
            final_accuracy: Final model accuracy percentage
            metrics: Optional training metrics
            
        Returns:
            Updated TrainingJob
        """
        try:
            job = self.db.query(TrainingJob).filter(
                TrainingJob.job_id == job_id
            ).first()
            
            if not job:
                raise ValueError(f"Training job {job_id} not found")
            
            job.status = TrainingJobStatus.COMPLETED.value
            job.end_time = datetime.utcnow()
            job.progress_percentage = 100
            job.final_accuracy = final_accuracy

            if metrics:
                # Persist metrics as JSON text
                job.training_metrics = json.dumps(metrics)
            
            self.db.commit()
            self.db.refresh(job)
            
            logger.info(f"Completed training job {job_id} with accuracy {final_accuracy}")
            return job
            
        except Exception as e:
            logger.error(f"Error completing job {job_id}: {e}")
            self.db.rollback()
            raise
    
    def fail_job(
        self,
        job_id: str,
        error_message: str
    ) -> TrainingJob:
        """
        Mark job as failed
        
        Args:
            job_id: ID of the job
            error_message: Error description
            
        Returns:
            Updated TrainingJob
        """
        try:
            job = self.db.query(TrainingJob).filter(
                TrainingJob.job_id == job_id
            ).first()
            
            if not job:
                raise ValueError(f"Training job {job_id} not found")
            
            job.status = TrainingJobStatus.FAILED.value
            job.end_time = datetime.utcnow()
            job.error_message = error_message
            
            current_log = job.training_log or ""
            job.training_log = f"{current_log}\n[{datetime.utcnow()}] ERROR: {error_message}"
            
            self.db.commit()
            self.db.refresh(job)
            
            logger.error(f"Failed training job {job_id}: {error_message}")
            return job
            
        except Exception as e:
            logger.error(f"Error failing job {job_id}: {e}")
            self.db.rollback()
            raise
    
    def cancel_job(self, job_id: str) -> TrainingJob:
        """
        Cancel a running or queued job
        
        Args:
            job_id: ID of the job to cancel
            
        Returns:
            Updated TrainingJob
        """
        try:
            job = self.db.query(TrainingJob).filter(
                TrainingJob.job_id == job_id
            ).first()
            
            if not job:
                raise ValueError(f"Training job {job_id} not found")
            
            if job.status in [TrainingJobStatus.COMPLETED.value, TrainingJobStatus.FAILED.value]:
                raise ValueError(f"Cannot cancel {job.status} job")
            
            job.status = TrainingJobStatus.FAILED.value
            job.end_time = datetime.utcnow()
            job.error_message = "Cancelled by user"
            
            self.db.commit()
            self.db.refresh(job)
            
            logger.info(f"Cancelled training job {job_id}")
            return job
            
        except Exception as e:
            logger.error(f"Error cancelling job {job_id}: {e}")
            self.db.rollback()
            raise
    
    def get_queued_jobs(self, limit: int = 10) -> List[TrainingJob]:
        """Get queued jobs ready to run"""
        try:
            jobs = self.db.query(TrainingJob).filter(
                TrainingJob.status == TrainingJobStatus.QUEUED.value
            ).order_by(TrainingJob.created_at.asc()).limit(limit).all()
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error getting queued jobs: {e}")
            return []
    
    def get_running_jobs(self) -> List[TrainingJob]:
        """Get currently running jobs"""
        try:
            jobs = self.db.query(TrainingJob).filter(
                TrainingJob.status == TrainingJobStatus.RUNNING.value
            ).all()
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error getting running jobs: {e}")
            return []
    
    def prepare_dataset(self, job_id: str) -> Dict:
        """
        Prepare training dataset for a job
        
        Args:
            job_id: ID of the training job
            
        Returns:
            Dataset statistics and file paths
        """
        try:
            job = self.db.query(TrainingJob).filter(
                TrainingJob.job_id == job_id
            ).first()
            
            if not job:
                raise ValueError(f"Training job {job_id} not found")
            
            # Query validated and anonymized cases
            cases = self.db.query(ValidatedCase).filter(
                ValidatedCase.validation_status == ValidationStatus.VALIDATED.value,
                ValidatedCase.is_anonymized == True,
                ValidatedCase.used_in_training == False  # Don't reuse in same job
            ).all()
            
            # Mark cases as used
            for case in cases:
                case.used_in_training = True
            
            self.db.commit()
            
            return {
                "job_id": job_id,
                "total_cases": len(cases),
                "dataset_ready": True,
                "message": f"Prepared {len(cases)} cases for training"
            }
            
        except Exception as e:
            logger.error(f"Error preparing dataset for {job_id}: {e}")
            self.db.rollback()
            raise
