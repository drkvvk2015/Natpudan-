"""
Medical Named Entity Recognition (NER) Service
Extracts clinical entities from medical text using scispacy + domain-specific models.

scispacy: High-performance NLP library for scientific/medical documents
- Trained on biomedical literature and clinical notes
- Recognizes entities: DISEASE, DRUG, TREATMENT, PROCEDURE, SYMPTOM, etc.
- Much faster and more accurate than generic NER on medical text

Entity types recognized:
- DISEASE: Medical conditions and disorders
- DRUG: Medications and pharmaceutical agents
- TREATMENT: Medical interventions and therapies
- PROCEDURE: Medical procedures and tests
- SYMPTOM: Patient symptoms and clinical findings
- ANATOMICAL_SITE: Body parts and anatomical regions
- MEASUREMENT: Clinical measurements and lab values

Usage:
    ner = MedicalNER()
    entities = ner.extract_entities(text)  # Extract all entities
    diseases = ner.extract_entities(text, entity_types=["DISEASE"])  # Filter by type
"""

import logging
from typing import List, Dict, Any, Optional, Set
import re

logger = logging.getLogger(__name__)

# Medical entity type definitions
ENTITY_TYPES = {
    "DISEASE": "Medical conditions, disorders, and diseases",
    "DRUG": "Medications, pharmaceutical agents, and compounds",
    "TREATMENT": "Medical interventions, therapies, and treatments",
    "PROCEDURE": "Medical procedures, tests, and interventions",
    "SYMPTOM": "Patient symptoms, signs, and clinical findings",
    "ANATOMICAL_SITE": "Body parts, organs, and anatomical regions",
    "MEASUREMENT": "Clinical measurements, values, and lab results"
}

# Medical terminology patterns (fallback regex-based extraction)
MEDICAL_PATTERNS = {
    "DISEASE": [
        r"(?:disease|disorder|syndrome|condition|illness|infection|cancer|diabetes|hypertension|pneumonia|heart attack|stroke|obesity)",
        r"(?:arthritis|asthma|anemia|depression|anxiety|bipolar|schizophrenia|alzheimer|parkinson)"
    ],
    "DRUG": [
        r"(?:aspirin|ibuprofen|metformin|lisinopril|atorvastatin|omeprazole|amoxicillin|penicillin)",
        r"(?:\w+cillin|\w+floxacin|\w+pril|\w+statin|\w+azine)"  # Common drug suffixes
    ],
    "SYMPTOM": [
        r"(?:fever|cough|headache|chest pain|nausea|vomiting|diarrhea|fatigue|weakness|dizziness)",
        r"(?:shortness of breath|difficulty breathing|back pain|joint pain|muscle pain)"
    ],
    "PROCEDURE": [
        r"(?:surgery|biopsy|endoscopy|x-ray|mri|ct scan|ultrasound|laboratory test|blood test)",
        r"(?:appendectomy|bypass|transplant|dialysis|chemotherapy|radiation|vaccine)"
    ]
}


class MedicalNER:
    """
    Medical Named Entity Recognition service using scispacy and pattern-based extraction.
    
    Extracts clinical entities from medical text with support for multiple recognition methods:
    1. Rule-based patterns (fallback, always available)
    2. scispacy models (if installed - requires: pip install scispacy)
    """
    
    def __init__(self, use_scispacy: bool = True):
        """
        Initialize Medical NER.
        
        Args:
            use_scispacy: Whether to use scispacy if available (fallback to regex if not)
        """
        self.nlp = None
        self.use_scispacy = use_scispacy
        self.entity_count = {}  # Statistics
        
        if use_scispacy:
            self._init_scispacy()
    
    def _init_scispacy(self):
        """Initialize scispacy models"""
        try:
            import spacy
            logger.info("Loading scispacy biomedical NLP model...")
            
            # Try to load pre-built scispacy model
            try:
                self.nlp = spacy.load("en_ner_bc5cdr_md")
                logger.info("✅ Loaded scispacy biomedical NER model (BC5CDR)")
            except OSError:
                logger.warning("⚠️  scispacy model not found. Falling back to regex-based extraction.")
                self.nlp = None
        
        except ImportError:
            logger.warning("⚠️  scispacy not installed. Falling back to regex-based extraction. "
                          "Install with: pip install scispacy")
            self.nlp = None
    
    def extract_entities(
        self,
        text: str,
        entity_types: Optional[List[str]] = None,
        min_length: int = 2
    ) -> Dict[str, Any]:
        """
        Extract medical entities from text.
        
        Args:
            text: Medical text to process
            entity_types: Filter to specific entity types (if None, extract all)
            min_length: Minimum entity token count
            
        Returns:
            Dictionary with:
                - entities: List of extracted entities with type, text, confidence
                - entity_types: List of detected entity types
                - entity_count: Count per entity type
                - total_entities: Total unique entities
        """
        if not text or not isinstance(text, str):
            return {
                "entities": [],
                "entity_types": [],
                "entity_count": {},
                "total_entities": 0
            }
        
        # Use scispacy if available, fallback to regex
        if self.nlp:
            entities = self._extract_scispacy(text, entity_types, min_length)
        else:
            entities = self._extract_regex(text, entity_types, min_length)
        
        # Calculate statistics
        entity_count = {}
        for entity in entities:
            entity_type = entity["type"]
            entity_count[entity_type] = entity_count.get(entity_type, 0) + 1
        
        detected_types = list(set([e["type"] for e in entities]))
        
        return {
            "entities": entities,
            "entity_types": detected_types,
            "entity_count": entity_count,
            "total_entities": len(set((e["text"], e["type"]) for e in entities))  # Unique count
        }
    
    def _extract_scispacy(
        self,
        text: str,
        entity_types: Optional[List[str]] = None,
        min_length: int = 2
    ) -> List[Dict[str, Any]]:
        """Extract entities using scispacy model"""
        entities = []
        
        try:
            doc = self.nlp(text)
            
            for ent in doc.ents:
                # Map scispacy entity labels to our standard types
                entity_type = self._map_scispacy_label(ent.label_)
                
                if entity_type and (not entity_types or entity_type in entity_types):
                    if len(ent.text.split()) >= min_length:
                        entities.append({
                            "text": ent.text.strip(),
                            "type": entity_type,
                            "start": ent.start_char,
                            "end": ent.end_char,
                            "confidence": 0.95  # scispacy doesn't provide confidence
                        })
        
        except Exception as e:
            logger.error(f"❌ Error in scispacy extraction: {e}")
        
        return entities
    
    def _extract_regex(
        self,
        text: str,
        entity_types: Optional[List[str]] = None,
        min_length: int = 2
    ) -> List[Dict[str, Any]]:
        """Extract entities using regex patterns (fallback)"""
        entities = []
        
        for entity_type, patterns in MEDICAL_PATTERNS.items():
            if entity_types and entity_type not in entity_types:
                continue
            
            for pattern in patterns:
                try:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        matched_text = match.group(0).strip()
                        
                        if len(matched_text.split()) >= min_length:
                            entities.append({
                                "text": matched_text,
                                "type": entity_type,
                                "start": match.start(),
                                "end": match.end(),
                                "confidence": 0.75  # Regex-based has lower confidence
                            })
                
                except Exception as e:
                    logger.debug(f"Regex pattern error: {e}")
        
        # Deduplicate and sort by position
        unique_entities = {}
        for entity in entities:
            key = (entity["start"], entity["end"])
            if key not in unique_entities or entity["confidence"] > unique_entities[key]["confidence"]:
                unique_entities[key] = entity
        
        return sorted(unique_entities.values(), key=lambda x: x["start"])
    
    def _map_scispacy_label(self, label: str) -> Optional[str]:
        """Map scispacy entity labels to standard types"""
        mapping = {
            "DISEASE": "DISEASE",
            "CHEMICAL": "DRUG",
            "DRUG": "DRUG",
            "GENE": "ANATOMICAL_SITE",
            "TREATMENT": "TREATMENT",
            "PROCEDURE": "PROCEDURE",
            "SYMPTOM": "SYMPTOM",
            "BODY_PART": "ANATOMICAL_SITE"
        }
        return mapping.get(label, label)
    
    def get_entity_distribution(self, text: str) -> Dict[str, int]:
        """Get distribution of entity types in text"""
        result = self.extract_entities(text)
        return result["entity_count"]
    
    def check_medical_relevance(self, text: str, min_entities: int = 3) -> Dict[str, Any]:
        """
        Check if text has sufficient medical content.
        
        Args:
            text: Text to check
            min_entities: Minimum required medical entities
            
        Returns:
            Dictionary with:
                - is_medical: Whether text is medically relevant
                - entity_count: Number of extracted entities
                - entity_diversity: Number of different entity types
                - confidence: Overall medical relevance confidence
        """
        result = self.extract_entities(text)
        
        entity_count = result["total_entities"]
        entity_diversity = len(result["entity_types"])
        
        # Calculate confidence
        confidence = min(entity_count / max(min_entities, 1), 1.0) * min(entity_diversity / 3, 1.0)
        
        return {
            "is_medical": entity_count >= min_entities,
            "entity_count": entity_count,
            "entity_diversity": entity_diversity,
            "confidence": confidence
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get NER processing statistics"""
        return {
            "use_scispacy": self.nlp is not None,
            "entity_types_supported": list(ENTITY_TYPES.keys()),
            "fallback_method": "regex" if self.nlp is None else "scispacy"
        }


def get_medical_ner() -> MedicalNER:
    """Factory function to get Medical NER instance"""
    return MedicalNER(use_scispacy=True)
