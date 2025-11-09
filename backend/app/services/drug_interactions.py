"""
Drug Interaction Checker Service
Provides rule-based drug interaction detection with severity classification
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import re

logger = logging.getLogger(__name__)


class DrugInteractionChecker:
    """
    Rule-based drug interaction checker with severity classification
    In production, integrate with comprehensive drug databases like DrugBank or RxNorm
    """
    
    # Common high-risk drug interactions (non-exhaustive, for demonstration)
    INTERACTIONS_DB = {
        # Warfarin interactions
        ("warfarin", "aspirin"): {
            "severity": "high",
            "description": "Increased risk of bleeding",
            "mechanism": "Both drugs affect blood clotting",
            "recommendation": "Monitor INR closely, consider alternative antiplatelet if possible"
        },
        ("warfarin", "nsaid"): {
            "severity": "high",
            "description": "Significantly increased bleeding risk",
            "mechanism": "NSAIDs inhibit platelet function and may displace warfarin from protein binding",
            "recommendation": "Avoid combination, use acetaminophen for pain management"
        },
        ("warfarin", "amiodarone"): {
            "severity": "high",
            "description": "Increased warfarin effect and bleeding risk",
            "mechanism": "Amiodarone inhibits CYP2C9, reducing warfarin metabolism",
            "recommendation": "Reduce warfarin dose by 30-50%, monitor INR closely"
        },
        
        # QT prolongation combinations
        ("amiodarone", "azithromycin"): {
            "severity": "high",
            "description": "Risk of QT prolongation and torsades de pointes",
            "mechanism": "Both drugs prolong QT interval",
            "recommendation": "Avoid combination, monitor ECG if unavoidable, check electrolytes"
        },
        ("azithromycin", "ondansetron"): {
            "severity": "moderate",
            "description": "Potential QT prolongation",
            "mechanism": "Additive effect on cardiac repolarization",
            "recommendation": "Use with caution, consider ECG monitoring in high-risk patients"
        },
        
        # ACE inhibitor + K-sparing diuretic
        ("lisinopril", "spironolactone"): {
            "severity": "moderate",
            "description": "Risk of hyperkalemia",
            "mechanism": "Both drugs increase serum potassium",
            "recommendation": "Monitor potassium levels regularly, adjust doses as needed"
        },
        ("enalapril", "spironolactone"): {
            "severity": "moderate",
            "description": "Risk of hyperkalemia",
            "mechanism": "Both drugs increase serum potassium",
            "recommendation": "Monitor potassium levels regularly"
        },
        
        # Diabetes medications
        ("metformin", "glipizide"): {
            "severity": "low",
            "description": "Additive glucose-lowering effect",
            "mechanism": "Different mechanisms, synergistic effect",
            "recommendation": "Monitor blood glucose, adjust doses to avoid hypoglycemia"
        },
        ("insulin", "metformin"): {
            "severity": "low",
            "description": "Enhanced glucose control but increased hypoglycemia risk",
            "mechanism": "Complementary mechanisms",
            "recommendation": "Monitor blood glucose closely, patient education on hypoglycemia"
        },
        
        # Antibiotic interactions
        ("ciprofloxacin", "tizanidine"): {
            "severity": "high",
            "description": "Severe hypotension and sedation",
            "mechanism": "Ciprofloxacin inhibits CYP1A2, dramatically increasing tizanidine levels",
            "recommendation": "Contraindicated - do not use together"
        },
        ("clarithromycin", "simvastatin"): {
            "severity": "high",
            "description": "Risk of rhabdomyolysis",
            "mechanism": "Clarithromycin inhibits CYP3A4, increasing statin levels",
            "recommendation": "Avoid combination or suspend statin during antibiotic course"
        },
        
        # Antihypertensive combinations (usually beneficial)
        ("amlodipine", "lisinopril"): {
            "severity": "low",
            "description": "Additive blood pressure lowering",
            "mechanism": "Complementary mechanisms (CCB + ACE inhibitor)",
            "recommendation": "Generally safe combination, monitor blood pressure"
        },
        ("hydrochlorothiazide", "lisinopril"): {
            "severity": "low",
            "description": "Enhanced blood pressure control",
            "mechanism": "Synergistic antihypertensive effect",
            "recommendation": "Standard combination, monitor BP and electrolytes"
        },
    }
    
    # Drug class patterns for grouping
    DRUG_CLASSES = {
        "nsaid": ["ibuprofen", "naproxen", "diclofenac", "celecoxib", "indomethacin", "ketorolac"],
        "ace_inhibitor": ["lisinopril", "enalapril", "ramipril", "captopril", "benazepril"],
        "statin": ["atorvastatin", "simvastatin", "rosuvastatin", "pravastatin", "lovastatin"],
        "macrolide": ["azithromycin", "clarithromycin", "erythromycin"],
        "fluoroquinolone": ["ciprofloxacin", "levofloxacin", "moxifloxacin"],
        "beta_blocker": ["metoprolol", "atenolol", "carvedilol", "bisoprolol", "propranolol"],
    }
    
    def __init__(self):
        """Initialize the drug interaction checker"""
        self.normalized_db = self._build_normalized_db()
    
    def _normalize_drug_name(self, drug: str) -> str:
        """Extract base drug name from string (remove dosage, route, etc.)"""
        # Remove common patterns: dosage, route, brand names
        drug_lower = drug.lower().strip()
        # Remove dosage patterns (e.g., "5mg", "10 mg", "500mg/day")
        drug_lower = re.sub(r'\d+\s*(mg|mcg|g|ml|units?|iu).*$', '', drug_lower)
        # Remove route/form patterns
        drug_lower = re.sub(r'\b(tablet|capsule|injection|oral|iv|po|sc|im)s?\b', '', drug_lower)
        # Remove extra whitespace
        drug_lower = ' '.join(drug_lower.split()).strip()
        return drug_lower
    
    def _get_drug_class(self, drug_name: str) -> Optional[str]:
        """Determine drug class if applicable"""
        normalized = self._normalize_drug_name(drug_name)
        for drug_class, members in self.DRUG_CLASSES.items():
            if normalized in members or any(member in normalized for member in members):
                return drug_class
        return None
    
    def _build_normalized_db(self) -> Dict[Tuple[str, str], Dict[str, Any]]:
        """Build a normalized interaction database including class-based interactions"""
        normalized = {}
        for (drug1, drug2), interaction in self.INTERACTIONS_DB.items():
            normalized[(drug1, drug2)] = interaction
            normalized[(drug2, drug1)] = interaction  # Bidirectional
        return normalized
    
    def check_interaction(self, drug1: str, drug2: str) -> Optional[Dict[str, Any]]:
        """
        Check for interaction between two drugs
        
        Args:
            drug1: First drug name
            drug2: Second drug name
            
        Returns:
            Interaction details if found, None otherwise
        """
        norm1 = self._normalize_drug_name(drug1)
        norm2 = self._normalize_drug_name(drug2)
        
        # Direct lookup
        interaction = self.normalized_db.get((norm1, norm2))
        if interaction:
            return {
                "drug1": drug1,
                "drug2": drug2,
                **interaction
            }
        
        # Class-based lookup
        class1 = self._get_drug_class(drug1)
        class2 = self._get_drug_class(drug2)
        
        if class1:
            interaction = self.normalized_db.get((class1, norm2))
            if interaction:
                return {
                    "drug1": drug1,
                    "drug2": drug2,
                    **interaction
                }
        
        if class2:
            interaction = self.normalized_db.get((norm1, class2))
            if interaction:
                return {
                    "drug1": drug1,
                    "drug2": drug2,
                    **interaction
                }
        
        return None
    
    def check_multiple_drugs(
        self,
        medications: List[str],
        include_severity: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Check for interactions among a list of medications
        
        Args:
            medications: List of medication names
            include_severity: Optional list of severities to filter (e.g., ["high", "moderate"])
            
        Returns:
            Dictionary with interaction results
        """
        interactions = []
        checked_pairs = set()
        
        # Check all pairs
        for i, drug1 in enumerate(medications):
            for drug2 in medications[i+1:]:
                # Avoid duplicate checks
                pair = tuple(sorted([drug1.lower(), drug2.lower()]))
                if pair in checked_pairs:
                    continue
                checked_pairs.add(pair)
                
                interaction = self.check_interaction(drug1, drug2)
                if interaction:
                    # Filter by severity if specified
                    if include_severity and interaction["severity"] not in include_severity:
                        continue
                    interactions.append(interaction)
        
        # Categorize by severity
        severity_counts = {
            "high": len([i for i in interactions if i["severity"] == "high"]),
            "moderate": len([i for i in interactions if i["severity"] == "moderate"]),
            "low": len([i for i in interactions if i["severity"] == "low"])
        }
        
        return {
            "medications_checked": medications,
            "total_interactions": len(interactions),
            "interactions": interactions,
            "severity_breakdown": severity_counts,
            "high_risk_warning": severity_counts["high"] > 0
        }
    
    def get_all_interactions_for_drug(self, drug_name: str) -> List[Dict[str, Any]]:
        """
        Get all known interactions for a specific drug
        
        Args:
            drug_name: Drug name to check
            
        Returns:
            List of all known interactions
        """
        normalized = self._normalize_drug_name(drug_name)
        interactions = []
        
        for (drug1, drug2), interaction in self.normalized_db.items():
            if drug1 == normalized or drug2 == normalized:
                other_drug = drug2 if drug1 == normalized else drug1
                interactions.append({
                    "interacting_drug": other_drug,
                    **interaction
                })
        
        return interactions


# Singleton instance
_drug_checker_instance = None


def get_drug_checker() -> DrugInteractionChecker:
    """Get or create singleton drug interaction checker instance"""
    global _drug_checker_instance
    if _drug_checker_instance is None:
        _drug_checker_instance = DrugInteractionChecker()
    return _drug_checker_instance
