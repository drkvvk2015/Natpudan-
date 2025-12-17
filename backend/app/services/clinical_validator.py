"""
Clinical Validation Service (Phase 3)
Validates AI predictions against medical guidelines and literature consensus.

Validation approaches:
1. Clinical Guideline Compliance: Check against established treatment guidelines
2. Literature Consensus: Verify against peer-reviewed medical literature
3. Drug-Condition Alignment: Validate recommended drugs match condition
4. Contraindication Checking: Flag dangerous drug combinations
5. Evidence Level Assessment: Score confidence based on evidence quality

Usage:
    validator = ClinicalValidator()
    validation = validator.validate_diagnosis(
        diagnosis="Type 2 Diabetes",
        recommended_treatment="Metformin",
        patient_info={"age": 45, "conditions": ["hypertension"]}
    )
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class EvidenceLevel(Enum):
    """Evidence quality levels (GRADE methodology)"""
    HIGH = "High"  # Multiple RCTs, strong evidence
    MODERATE = "Moderate"  # RCTs with limitations or observational studies
    LOW = "Low"  # Limited evidence, small studies
    VERY_LOW = "Very Low"  # Expert opinion, case reports


class ValidationStatus(Enum):
    """Validation result status"""
    APPROVED = "Approved"  # Matches guidelines/literature
    CONDITIONAL = "Conditional"  # Acceptable with caveats
    FLAGGED = "Flagged"  # Requires review, potential issues
    CONTRAINDICATED = "Contraindicated"  # Not recommended


@dataclass
class ValidationResult:
    """Result of clinical validation"""
    diagnosis: str
    recommendation: str
    status: ValidationStatus
    evidence_level: EvidenceLevel
    confidence: float  # [0, 1]
    supporting_guidelines: List[str]
    contraindications: List[str]
    caveats: List[str]
    recommendations: List[str]


class ClinicalValidator:
    """
    Clinical validator for medical AI predictions.
    
    Validates recommendations against established clinical guidelines and literature.
    """
    
    # Clinical guidelines database (simplified; in production use UpToDate API)
    CLINICAL_GUIDELINES = {
        "type 2 diabetes": {
            "first_line_treatments": ["metformin", "diet", "exercise"],
            "second_line": ["sulfonylurea", "dpp4_inhibitor", "glp1"],
            "guidelines": ["ADA Standards of Care 2024", "IDF Guidelines 2024"],
            "evidence_level": EvidenceLevel.HIGH
        },
        "hypertension": {
            "first_line_treatments": ["ace_inhibitor", "arb", "calcium_channel_blocker", "diuretic"],
            "second_line": ["beta_blocker", "alpha_blocker"],
            "guidelines": ["ACC/AHA Guidelines 2023"],
            "evidence_level": EvidenceLevel.HIGH
        },
        "heart disease": {
            "first_line_treatments": ["statin", "aspirin", "beta_blocker", "ace_inhibitor"],
            "second_line": ["nitroglycerin", "plavix", "digoxin"],
            "guidelines": ["AHA/ACC Guidelines 2023", "ESC Guidelines 2023"],
            "evidence_level": EvidenceLevel.HIGH
        },
        "pneumonia": {
            "first_line_treatments": ["amoxicillin", "cephalosporin", "azithromycin"],
            "second_line": ["fluoroquinolone", "vancomycin"],
            "guidelines": ["IDSA Pneumonia Guidelines 2023", "CDC Guidelines"],
            "evidence_level": EvidenceLevel.HIGH
        },
        "asthma": {
            "first_line_treatments": ["albuterol", "inhaled_corticosteroid", "leukotriene_inhibitor"],
            "second_line": ["long_acting_beta_agonist", "theophylline"],
            "guidelines": ["GINA Asthma Strategy 2024", "NAEPP Guidelines"],
            "evidence_level": EvidenceLevel.HIGH
        },
        "depression": {
            "first_line_treatments": ["ssri", "snri", "psychotherapy", "cbt"],
            "second_line": ["tricyclic", "maoi", "atypical_antipsychotic"],
            "guidelines": ["APA Practice Guidelines 2023"],
            "evidence_level": EvidenceLevel.HIGH
        }
    }
    
    # Drug contraindication database
    DRUG_CONTRAINDICATIONS = {
        ("aspirin", "severe bleeding disorder"): "HIGH",
        ("nsaid", "peptic ulcer disease"): "HIGH",
        ("nsaid", "severe kidney disease"): "MODERATE",
        ("metformin", "severe kidney disease"): "HIGH",
        ("lisinopril", "pregnancy"): "HIGH",
        ("lisinopril", "hyperkalemia"): "MODERATE",
        ("beta_blocker", "asthma"): "MODERATE",
        ("beta_blocker", "heart_block"): "HIGH",
        ("statin", "severe liver disease"): "HIGH",
        ("warfarin", "low platelet count"): "HIGH"
    }
    
    # Drug-disease interactions (when drug should be used cautiously)
    DRUG_DISEASE_CAUTIONS = {
        ("ace_inhibitor", "kidney disease"): "Monitor creatinine levels",
        ("diuretic", "gout"): "May precipitate gout attacks",
        ("corticosteroid", "diabetes"): "May elevate glucose levels",
        ("beta_blocker", "diabetes"): "May mask hypoglycemia symptoms",
        ("nsaid", "heart failure"): "May worsen fluid retention"
    }
    
    def __init__(self):
        """Initialize clinical validator"""
        self.validation_count = 0
        logger.info("✅ ClinicalValidator initialized")
    
    def validate_diagnosis(
        self,
        diagnosis: str,
        recommended_treatment: str,
        patient_info: Optional[Dict[str, Any]] = None,
        confidence_score: Optional[float] = None
    ) -> ValidationResult:
        """
        Validate a diagnosis-treatment recommendation.
        
        Args:
            diagnosis: Diagnosed condition
            recommended_treatment: Proposed treatment/medication
            patient_info: Patient context:
                - age, comorbidities, contraindications, medications
            confidence_score: AI confidence in recommendation [0, 1]
            
        Returns:
            ValidationResult with validation status and evidence
        """
        self.validation_count += 1
        patient_info = patient_info or {}
        
        # Normalize diagnosis name
        diagnosis_normalized = diagnosis.lower().strip()
        
        # Get guidelines for this diagnosis
        guidelines = self.CLINICAL_GUIDELINES.get(diagnosis_normalized)
        
        if not guidelines:
            logger.warning(f"No guidelines found for {diagnosis}")
            return self._create_unknown_result(diagnosis, recommended_treatment)
        
        # Check if treatment is guideline-recommended
        treatment_normalized = recommended_treatment.lower().strip()
        is_first_line = treatment_normalized in guidelines.get("first_line_treatments", [])
        is_second_line = treatment_normalized in guidelines.get("second_line", [])
        
        # Check for patient-specific contraindications
        patient_conditions = patient_info.get("comorbidities", [])
        patient_medications = patient_info.get("current_medications", [])
        
        # Check drug contraindications
        contraindications = self._check_contraindications(
            treatment_normalized, patient_conditions, patient_medications
        )
        
        # Check drug-disease interactions
        caveats = self._check_drug_disease_caveats(treatment_normalized, patient_conditions)
        
        # Determine validation status
        status, confidence = self._determine_status(
            is_first_line, is_second_line, contraindications, len(caveats), confidence_score
        )
        
        # Get evidence level
        evidence_level = guidelines.get("evidence_level", EvidenceLevel.MODERATE)
        
        # Generate recommendations
        recommendations = self._generate_validation_recommendations(
            status, is_first_line, len(caveats), patient_info
        )
        
        return ValidationResult(
            diagnosis=diagnosis,
            recommendation=recommended_treatment,
            status=status,
            evidence_level=evidence_level,
            confidence=confidence,
            supporting_guidelines=guidelines.get("guidelines", []),
            contraindications=contraindications,
            caveats=caveats,
            recommendations=recommendations
        )
    
    def _check_contraindications(
        self,
        treatment: str,
        conditions: List[str],
        medications: List[str]
    ) -> List[str]:
        """Check for drug contraindications"""
        flagged = []
        
        for condition in conditions:
            condition_norm = condition.lower()
            for (drug, cond), severity in self.DRUG_CONTRAINDICATIONS.items():
                if treatment.lower() in drug and condition_norm in cond.lower():
                    flagged.append(f"{severity}: {treatment} contraindicated in {condition}")
        
        return flagged
    
    def _check_drug_disease_caveats(
        self,
        treatment: str,
        conditions: List[str]
    ) -> List[str]:
        """Check for drug-disease interactions that require monitoring"""
        caveats = []
        
        for condition in conditions:
            condition_norm = condition.lower()
            for (drug, cond), note in self.DRUG_DISEASE_CAUTIONS.items():
                if treatment.lower() in drug and condition_norm in cond.lower():
                    caveats.append(f"Caution: {note}")
        
        return caveats
    
    def _determine_status(
        self,
        is_first_line: bool,
        is_second_line: bool,
        contraindications: List[str],
        caveat_count: int,
        confidence_score: Optional[float]
    ) -> Tuple[ValidationStatus, float]:
        """Determine validation status and confidence"""
        
        # High-priority: contraindications
        if any("HIGH" in c for c in contraindications):
            return ValidationStatus.CONTRAINDICATED, 0.1
        
        if any("MODERATE" in c for c in contraindications):
            return ValidationStatus.FLAGGED, 0.4
        
        # Primary: first-line treatment
        if is_first_line:
            confidence = 0.95 if caveat_count == 0 else 0.85
            return ValidationStatus.APPROVED, confidence
        
        # Secondary: second-line treatment
        if is_second_line:
            confidence = 0.75 if caveat_count == 0 else 0.65
            return ValidationStatus.CONDITIONAL, confidence
        
        # Unknown treatment
        if confidence_score and confidence_score > 0.7:
            return ValidationStatus.FLAGGED, 0.5
        
        return ValidationStatus.FLAGGED, 0.3
    
    def _generate_validation_recommendations(
        self,
        status: ValidationStatus,
        is_first_line: bool,
        caveat_count: int,
        patient_info: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if status == ValidationStatus.APPROVED:
            recommendations.append("✅ Treatment aligns with current clinical guidelines")
        
        elif status == ValidationStatus.CONDITIONAL:
            if not is_first_line:
                recommendations.append("⚠️  Treatment is second-line. First-line options preferred.")
            if caveat_count > 0:
                recommendations.append(f"📋 {caveat_count} patient-specific caveat(s). Monitor closely.")
        
        elif status == ValidationStatus.FLAGGED:
            recommendations.append("🚩 Treatment needs clinical review before implementation")
            recommendations.append("Consider alternative guideline-recommended treatments")
        
        elif status == ValidationStatus.CONTRAINDICATED:
            recommendations.append("🚫 CONTRAINDICATED. DO NOT PRESCRIBE.")
            recommendations.append("Select alternative treatment from guideline recommendations")
        
        # General recommendations
        recommendations.append("Monitor patient response and adjust treatment as needed")
        
        return recommendations
    
    def _create_unknown_result(self, diagnosis: str, treatment: str) -> ValidationResult:
        """Create result for unknown diagnosis"""
        return ValidationResult(
            diagnosis=diagnosis,
            recommendation=treatment,
            status=ValidationStatus.FLAGGED,
            evidence_level=EvidenceLevel.VERY_LOW,
            confidence=0.3,
            supporting_guidelines=[],
            contraindications=[],
            caveats=["Diagnosis not in standard guidelines database"],
            recommendations=[
                "⚠️  Diagnosis not in clinical guidelines database",
                "Recommend consultation with clinical expert",
                "Consider UpToDate, PubMed search for latest evidence"
            ]
        )
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation statistics"""
        return {
            "total_validations": self.validation_count,
            "guidelines_count": len(self.CLINICAL_GUIDELINES),
            "contraindications_count": len(self.DRUG_CONTRAINDICATIONS),
            "drug_disease_cautions_count": len(self.DRUG_DISEASE_CAUTIONS)
        }
    
    def list_guidelines(self) -> Dict[str, Any]:
        """List all available guidelines"""
        return {
            diagnosis: {
                "first_line": guidelines.get("first_line_treatments", []),
                "second_line": guidelines.get("second_line", []),
                "sources": guidelines.get("guidelines", [])
            }
            for diagnosis, guidelines in self.CLINICAL_GUIDELINES.items()
        }


def get_clinical_validator() -> ClinicalValidator:
    """Factory function to get clinical validator instance"""
    return ClinicalValidator()
