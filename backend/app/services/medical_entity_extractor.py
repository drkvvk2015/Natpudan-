"""
Medical Entity Extraction Service
Extracts diseases, medications, procedures, symptoms using NLP
"""

import logging
import re
from typing import List, Dict, Any, Set
from collections import defaultdict

logger = logging.getLogger(__name__)


class MedicalEntityExtractor:
    """
    Extracts medical entities from text using pattern matching and NLP.
    Identifies: diseases, medications, procedures, symptoms, lab tests, etc.
    """
    
    def __init__(self):
        """Initialize medical entity extractor"""
        
        # Common medication suffixes
        self.medication_patterns = [
            r'\b\w+(cillin|mycin|oxacin|azole|prazole|vir|statin|pril|sartan|olol)\b',
            r'\b(aspirin|ibuprofen|acetaminophen|metformin|insulin|warfarin)\b',
            r'\b\w+\s+\d+\s*mg\b',  # Medication with dosage
        ]
        
        # Common disease patterns
        self.disease_patterns = [
            r'\b(diabetes|hypertension|pneumonia|asthma|copd|cancer|stroke)\b',
            r'\b\w+(itis|osis|emia|pathy|trophy|plasia)\b',  # Medical suffixes
            r'\b(acute|chronic)\s+\w+\b',
        ]
        
        # Symptom patterns
        self.symptom_patterns = [
            r'\b(pain|fever|cough|nausea|vomiting|diarrhea|headache|fatigue)\b',
            r'\b(shortness of breath|chest pain|abdominal pain)\b',
            r'\b(dizziness|weakness|numbness|tingling)\b',
        ]
        
        # Procedure patterns
        self.procedure_patterns = [
            r'\b\w+(ectomy|otomy|oscopy|plasty|graphy|gram)\b',
            r'\b(surgery|operation|biopsy|catheterization|intubation)\b',
            r'\b(x-ray|ct scan|mri|ultrasound|ecg|ekg)\b',
        ]
        
        # Lab test patterns
        self.lab_test_patterns = [
            r'\b(cbc|bmp|cmp|hba1c|tsh|psa|crp|esr)\b',
            r'\b(blood test|urine test|culture|panel)\b',
            r'\b\w+\s+(level|count|rate)\b',
        ]
        
        # Vital sign patterns
        self.vital_patterns = [
            r'\b(blood pressure|bp|hr|heart rate|temperature|temp|spo2|oxygen saturation)\b',
            r'\b\d+/\d+\s*mmhg\b',  # Blood pressure
            r'\b\d+\s*bpm\b',  # Heart rate
            r'\b\d+\.?\d*\s*[cf]\b',  # Temperature
        ]
        
        logger.info("Medical entity extractor initialized")
    
    def extract_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract all medical entities from text.
        
        Args:
            text: Medical text
            
        Returns:
            Dictionary of entity types and their occurrences
        """
        text_lower = text.lower()
        
        entities = {
            "medications": self._extract_category(text_lower, self.medication_patterns),
            "diseases": self._extract_category(text_lower, self.disease_patterns),
            "symptoms": self._extract_category(text_lower, self.symptom_patterns),
            "procedures": self._extract_category(text_lower, self.procedure_patterns),
            "lab_tests": self._extract_category(text_lower, self.lab_test_patterns),
            "vitals": self._extract_category(text_lower, self.vital_patterns),
        }
        
        # Add frequency counts
        for category, items in entities.items():
            entities[category] = self._count_frequencies(items)
        
        return entities
    
    def _extract_category(
        self,
        text: str,
        patterns: List[str]
    ) -> List[str]:
        """Extract entities matching patterns"""
        found = set()
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entity = match.group(0).strip()
                if len(entity) > 2:  # Filter very short matches
                    found.add(entity)
        
        return list(found)
    
    def _count_frequencies(
        self,
        items: List[str]
    ) -> List[Dict[str, Any]]:
        """Count entity frequencies"""
        freq = defaultdict(int)
        for item in items:
            freq[item] += 1
        
        return [
            {"entity": entity, "count": count}
            for entity, count in sorted(
                freq.items(),
                key=lambda x: x[1],
                reverse=True
            )
        ]
    
    def extract_icd_codes(self, text: str) -> List[Dict[str, str]]:
        """
        Extract ICD-10 codes from text.
        
        Args:
            text: Medical text
            
        Returns:
            List of found ICD codes with context
        """
        # ICD-10 pattern: Letter followed by 2-3 digits, optional dot and 1-2 more digits
        pattern = r'\b([A-Z]\d{2}\.?\d{0,2})\b'
        
        codes = []
        for match in re.finditer(pattern, text):
            code = match.group(1)
            # Get surrounding context
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end].strip()
            
            codes.append({
                "code": code,
                "context": context,
                "position": match.start()
            })
        
        return codes
    
    def extract_dosages(self, text: str) -> List[Dict[str, str]]:
        """
        Extract medication dosages.
        
        Args:
            text: Medical text
            
        Returns:
            List of medications with dosages
        """
        # Pattern: medication name followed by dosage
        pattern = r'(\w+)\s+(\d+\.?\d*)\s*(mg|ml|mcg|g|units?)'
        
        dosages = []
        for match in re.finditer(pattern, text, re.IGNORECASE):
            medication = match.group(1)
            dose = match.group(2)
            unit = match.group(3)
            
            dosages.append({
                "medication": medication,
                "dose": f"{dose} {unit}",
                "dose_value": float(dose),
                "dose_unit": unit
            })
        
        return dosages
    
    def build_medical_summary(
        self,
        entities: Dict[str, List[Dict[str, Any]]]
    ) -> str:
        """
        Build human-readable summary from extracted entities.
        
        Args:
            entities: Extracted entities
            
        Returns:
            Formatted summary
        """
        lines = ["MEDICAL ENTITY SUMMARY", "=" * 50, ""]
        
        # Medications
        if entities.get("medications"):
            lines.append("MEDICATIONS:")
            for item in entities["medications"][:10]:
                lines.append(f"  - {item['entity']} (mentioned {item['count']}x)")
            lines.append("")
        
        # Diseases/Conditions
        if entities.get("diseases"):
            lines.append("DISEASES/CONDITIONS:")
            for item in entities["diseases"][:10]:
                lines.append(f"  - {item['entity']} (mentioned {item['count']}x)")
            lines.append("")
        
        # Symptoms
        if entities.get("symptoms"):
            lines.append("SYMPTOMS:")
            for item in entities["symptoms"][:10]:
                lines.append(f"  - {item['entity']} (mentioned {item['count']}x)")
            lines.append("")
        
        # Procedures
        if entities.get("procedures"):
            lines.append("PROCEDURES:")
            for item in entities["procedures"][:10]:
                lines.append(f"  - {item['entity']} (mentioned {item['count']}x)")
            lines.append("")
        
        # Lab Tests
        if entities.get("lab_tests"):
            lines.append("LAB TESTS:")
            for item in entities["lab_tests"][:10]:
                lines.append(f"  - {item['entity']} (mentioned {item['count']}x)")
            lines.append("")
        
        return "\n".join(lines)


# Global instance
_entity_extractor = None

def get_entity_extractor() -> MedicalEntityExtractor:
    """Get or create entity extractor instance"""
    global _entity_extractor
    if _entity_extractor is None:
        _entity_extractor = MedicalEntityExtractor()
    return _entity_extractor
