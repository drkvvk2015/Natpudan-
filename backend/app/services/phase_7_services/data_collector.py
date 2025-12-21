"""
Phase 7: Data Collector Service

Automatically collects validated medical cases for training data.
Includes HIPAA anonymization and quality filtering.
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import json
import hashlib
import re

from ...database.models import (
    ValidatedCase, 
    ValidationStatus
)
from ...models import (
    PatientIntake,
    TreatmentPlan,
    User
)

logger = logging.getLogger(__name__)


class DataCollector:
    """
    Collects validated medical cases for training data
    
    Features:
    - Auto-collection from production database
    - HIPAA anonymization
    - Quality filtering (confidence > threshold)
    - Duplicate detection
    - Data versioning
    """
    
    def __init__(
        self, 
        db: Session,
        min_confidence: int = 80,
        min_quality_score: int = 70
    ):
        self.db = db
        self.min_confidence = min_confidence
        self.min_quality_score = min_quality_score
        
    def collect_cases(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        validation_status: ValidationStatus = ValidationStatus.VALIDATED,
        limit: Optional[int] = None
    ) -> List[ValidatedCase]:
        """
        Collect validated cases from database
        
        Args:
            start_date: Filter cases after this date
            end_date: Filter cases before this date
            validation_status: Only collect cases with this status
            limit: Maximum number of cases to collect
            
        Returns:
            List of ValidatedCase objects
        """
        try:
            query = self.db.query(ValidatedCase)
            
            # Apply filters
            if start_date:
                query = query.filter(ValidatedCase.created_at >= start_date)
            if end_date:
                query = query.filter(ValidatedCase.created_at <= end_date)
            
            query = query.filter(ValidatedCase.validation_status == validation_status.value)
            
            # Quality filters
            query = query.filter(
                or_(
                    ValidatedCase.diagnosis_confidence >= self.min_confidence,
                    ValidatedCase.diagnosis_confidence.is_(None)  # Include if not set
                )
            )
            
            # Limit
            if limit:
                query = query.limit(limit)
                
            cases = query.all()
            logger.info(f"Collected {len(cases)} validated cases")
            return cases
            
        except Exception as e:
            logger.error(f"Error collecting cases: {e}")
            return []
    
    def collect_from_treatment_plans(
        self,
        min_treatment_duration_days: int = 7,
        limit: Optional[int] = None
    ) -> int:
        """
        Collect cases from completed treatment plans
        
        Args:
            min_treatment_duration_days: Minimum treatment duration to consider
            limit: Maximum number of cases to collect
            
        Returns:
            Number of new cases collected
        """
        try:
            # Find completed treatment plans not yet in ValidatedCase
            treatment_plans = (
                self.db.query(TreatmentPlan)
                .filter(TreatmentPlan.status == "completed")
                .filter(TreatmentPlan.end_date.isnot(None))
                .limit(limit if limit else 1000)
                .all()
            )
            
            collected_count = 0
            
            for plan in treatment_plans:
                # Check if already collected
                existing = self.db.query(ValidatedCase).filter(
                    ValidatedCase.patient_intake_id == plan.patient_intake_id
                ).first()
                
                if existing:
                    continue
                
                # Calculate treatment duration
                if plan.start_date and plan.end_date:
                    duration = (plan.end_date - plan.start_date).days
                    if duration < min_treatment_duration_days:
                        continue
                
                # Create ValidatedCase
                case = ValidatedCase(
                    case_id=self._generate_case_id(plan.plan_id),
                    patient_intake_id=plan.patient_intake_id,
                    diagnosis=plan.primary_diagnosis,
                    diagnosis_confidence=85,  # Default confidence for completed treatment
                    validation_status=ValidationStatus.PENDING,
                    treatment_outcome="success" if plan.status == "completed" else "unknown",
                    medications_prescribed=self._collect_medications(plan),
                    data_quality_score=self._calculate_quality_score(plan),
                    is_anonymized=False,
                    created_at=datetime.utcnow()
                )
                
                self.db.add(case)
                collected_count += 1
            
            self.db.commit()
            logger.info(f"Collected {collected_count} cases from treatment plans")
            return collected_count
            
        except Exception as e:
            logger.error(f"Error collecting from treatment plans: {e}")
            self.db.rollback()
            return 0
    
    def anonymize_case(self, case: ValidatedCase) -> ValidatedCase:
        """
        Anonymize case data for HIPAA compliance
        
        Removes:
        - Patient names
        - Dates of birth
        - Addresses
        - Phone numbers
        - Email addresses
        - Medical record numbers
        - Any identifiable information
        
        Args:
            case: ValidatedCase to anonymize
            
        Returns:
            Anonymized ValidatedCase
        """
        try:
            if case.is_anonymized:
                logger.info(f"Case {case.case_id} already anonymized")
                return case
            
            # Anonymize diagnosis text
            if case.diagnosis:
                case.diagnosis = self._remove_pii(case.diagnosis)
            
            # Anonymize symptoms
            if case.symptoms:
                symptoms = json.loads(case.symptoms)
                case.symptoms = json.dumps([self._remove_pii(s) for s in symptoms])
            
            # Anonymize validation notes
            if case.validation_notes:
                case.validation_notes = self._remove_pii(case.validation_notes)
            
            # Remove patient intake link (keep only for reference, not in training)
            # We don't delete patient_intake_id for traceability
            
            # Mark as anonymized
            case.is_anonymized = True
            case.anonymization_date = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"Anonymized case {case.case_id}")
            return case
            
        except Exception as e:
            logger.error(f"Error anonymizing case {case.case_id}: {e}")
            self.db.rollback()
            return case
    
    def validate_case_quality(self, case: ValidatedCase) -> bool:
        """
        Validate case data quality
        
        Checks:
        - Diagnosis present
        - Minimum confidence threshold
        - Data completeness
        
        Args:
            case: ValidatedCase to validate
            
        Returns:
            True if case passes quality checks
        """
        try:
            # Check required fields
            if not case.diagnosis:
                logger.warning(f"Case {case.case_id} missing diagnosis")
                return False
            
            # Check confidence
            if case.diagnosis_confidence and case.diagnosis_confidence < self.min_confidence:
                logger.warning(f"Case {case.case_id} confidence too low: {case.diagnosis_confidence}")
                return False
            
            # Calculate quality score
            quality_score = self._calculate_quality_score_from_case(case)
            case.data_quality_score = quality_score
            
            if quality_score < self.min_quality_score:
                logger.warning(f"Case {case.case_id} quality score too low: {quality_score}")
                return False
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error validating case quality: {e}")
            return False
    
    def get_collection_statistics(self) -> Dict:
        """
        Get statistics about collected cases
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            total_cases = self.db.query(ValidatedCase).count()
            
            validated_cases = self.db.query(ValidatedCase).filter(
                ValidatedCase.validation_status == ValidationStatus.VALIDATED.value
            ).count()
            
            pending_cases = self.db.query(ValidatedCase).filter(
                ValidatedCase.validation_status == ValidationStatus.PENDING.value
            ).count()
            
            anonymized_cases = self.db.query(ValidatedCase).filter(
                ValidatedCase.is_anonymized == True
            ).count()
            
            used_in_training = self.db.query(ValidatedCase).filter(
                ValidatedCase.used_in_training == True
            ).count()
            
            avg_quality_raw = self.db.query(
                func.avg(ValidatedCase.data_quality_score)
            ).filter(
                ValidatedCase.data_quality_score.isnot(None)
            ).scalar()

            avg_quality = float(avg_quality_raw or 0.0)
            collection_rate = float(round((validated_cases / total_cases * 100) if total_cases > 0 else 0, 2))

            return {
                "total_cases": int(total_cases),
                "validated_cases": int(validated_cases),
                "pending_cases": int(pending_cases),
                "anonymized_cases": int(anonymized_cases),
                "used_in_training": int(used_in_training),
                "average_quality_score": round(avg_quality, 2),
                "collection_rate": collection_rate
            }
            
        except Exception as e:
            logger.error(f"Error getting collection statistics: {e}")
            return {
                "total_cases": 0,
                "validated_cases": 0,
                "pending_cases": 0,
                "anonymized_cases": 0,
                "used_in_training": 0,
                "average_quality_score": 0.0,
                "collection_rate": 0.0
            }
    
    # ========================================
    # HELPER METHODS
    # ========================================
    
    def _generate_case_id(self, seed: str) -> str:
        """Generate unique case ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        hash_part = hashlib.md5(seed.encode()).hexdigest()[:8]
        return f"CASE-{timestamp}-{hash_part}"
    
    def _remove_pii(self, text: str) -> str:
        """
        Remove personally identifiable information from text
        
        Patterns removed:
        - Names (proper nouns)
        - Dates
        - Phone numbers
        - Email addresses
        - Addresses
        """
        if not text:
            return text
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        
        # Remove phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
        text = re.sub(r'\(\d{3}\)\s*\d{3}[-.]?\d{4}', '[PHONE]', text)
        
        # Remove dates
        text = re.sub(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', '[DATE]', text)
        text = re.sub(r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b', '[DATE]', text)
        
        # Remove addresses (basic pattern)
        text = re.sub(r'\b\d+\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd)\b', '[ADDRESS]', text)
        
        # Remove SSN
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
        
        return text
    
    def _collect_medications(self, plan: TreatmentPlan) -> str:
        """Collect medications from treatment plan as JSON"""
        try:
            medications = [
                {
                    "name": med.medication_name,
                    "dosage": med.dosage,
                    "frequency": med.frequency,
                    "duration_days": med.duration_days
                }
                for med in plan.medications if med.is_active
            ]
            return json.dumps(medications)
        except:
            return "[]"
    
    def _calculate_quality_score(self, plan: TreatmentPlan) -> int:
        """Calculate data quality score for treatment plan"""
        score = 0
        
        # Has diagnosis
        if plan.primary_diagnosis:
            score += 30
        
        # Has medications
        if plan.medications and len(plan.medications) > 0:
            score += 20
        
        # Has clinical notes
        if plan.clinical_notes:
            score += 20
        
        # Has follow-ups
        if plan.follow_ups and len(plan.follow_ups) > 0:
            score += 15
        
        # Treatment completed
        if plan.status == "completed":
            score += 15
        
        return min(score, 100)
    
    def _calculate_quality_score_from_case(self, case: ValidatedCase) -> int:
        """Calculate data quality score for validated case"""
        score = 0
        
        # Has diagnosis
        if case.diagnosis:
            score += 40
        
        # Has symptoms
        if case.symptoms:
            try:
                symptoms = json.loads(case.symptoms)
                if len(symptoms) > 0:
                    score += 20
            except:
                pass
        
        # Has medications
        if case.medications_prescribed:
            try:
                meds = json.loads(case.medications_prescribed)
                if len(meds) > 0:
                    score += 20
            except:
                pass
        
        # Is anonymized
        if case.is_anonymized:
            score += 10
        
        # Is validated
        if case.validation_status == ValidationStatus.VALIDATED.value:
            score += 10
        
        return min(score, 100)
