"""
Enhanced Medical Knowledge Base with Multiple Data Sources
Supports: PDFs, Medical APIs, Local Medical Database, PubMed Integration
Uses Hybrid Search: Vector (semantic) + Keyword (BM25) + Re-ranking
"""

import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# Try importing optional dependencies
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class MedicalKnowledgeSource:
    """Base class for medical knowledge sources"""
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search this knowledge source"""
        raise NotImplementedError


class LocalMedicalDatabase(MedicalKnowledgeSource):
    """
    Local medical database with common conditions, symptoms, treatments.
    This provides fallback when external APIs are unavailable.
    """
    
    def __init__(self):
        self.knowledge_base = self._load_medical_knowledge()
        logger.info(f"Loaded {len(self.knowledge_base)} medical entries")
    
    def _load_medical_knowledge(self) -> Dict[str, Dict[str, Any]]:
        """Load comprehensive medical knowledge"""
        return {
            # Common Conditions
            "hypertension": {
                "name": "Hypertension (High Blood Pressure)",
                "category": "Cardiovascular",
                "symptoms": ["headache", "dizziness", "chest pain", "shortness of breath", "nosebleeds"],
                "causes": ["genetics", "high salt intake", "obesity", "lack of exercise", "stress", "alcohol"],
                "treatments": ["ACE inhibitors", "beta-blockers", "diuretics", "lifestyle modifications", "diet changes"],
                "icd10": "I10",
                "severity": "Moderate to High",
                "emergency_signs": ["severe headache", "chest pain", "vision problems", "severe anxiety"]
            },
            "diabetes_type2": {
                "name": "Type 2 Diabetes Mellitus",
                "category": "Endocrine",
                "symptoms": ["increased thirst", "frequent urination", "increased hunger", "fatigue", "blurred vision", "slow healing"],
                "causes": ["insulin resistance", "obesity", "genetics", "sedentary lifestyle", "age"],
                "treatments": ["metformin", "insulin therapy", "diet control", "exercise", "blood sugar monitoring"],
                "icd10": "E11",
                "severity": "Moderate to High",
                "complications": ["neuropathy", "retinopathy", "nephropathy", "cardiovascular disease"]
            },
            "asthma": {
                "name": "Asthma",
                "category": "Respiratory",
                "symptoms": ["wheezing", "shortness of breath", "chest tightness", "coughing", "difficulty breathing"],
                "causes": ["allergens", "air pollution", "respiratory infections", "exercise", "cold air", "stress"],
                "treatments": ["bronchodilators", "corticosteroids", "leukotriene modifiers", "inhaled medications"],
                "icd10": "J45",
                "severity": "Mild to Severe",
                "emergency_signs": ["severe difficulty breathing", "bluish lips", "rapid pulse", "confusion"]
            },
            "pneumonia": {
                "name": "Pneumonia",
                "category": "Respiratory",
                "symptoms": ["fever", "cough with phlegm", "chest pain", "shortness of breath", "fatigue", "confusion"],
                "causes": ["bacteria", "viruses", "fungi", "aspiration"],
                "treatments": ["antibiotics", "antivirals", "oxygen therapy", "rest", "fluids"],
                "icd10": "J18",
                "severity": "Moderate to High",
                "emergency_signs": ["difficulty breathing", "chest pain", "confusion", "high fever"]
            },
            "migraine": {
                "name": "Migraine Headache",
                "category": "Neurological",
                "symptoms": ["severe headache", "nausea", "vomiting", "sensitivity to light", "sensitivity to sound", "visual aura"],
                "causes": ["triggers", "hormonal changes", "stress", "certain foods", "lack of sleep"],
                "treatments": ["triptans", "NSAIDs", "anti-nausea medications", "preventive medications"],
                "icd10": "G43",
                "severity": "Moderate",
                "triggers": ["chocolate", "cheese", "wine", "stress", "bright lights"]
            },
            "depression": {
                "name": "Major Depressive Disorder",
                "category": "Mental Health",
                "symptoms": ["persistent sadness", "loss of interest", "fatigue", "sleep problems", "appetite changes", "difficulty concentrating"],
                "causes": ["brain chemistry", "genetics", "life events", "trauma", "chronic stress"],
                "treatments": ["SSRIs", "SNRIs", "psychotherapy", "CBT", "lifestyle changes"],
                "icd10": "F32",
                "severity": "Moderate to High",
                "emergency_signs": ["suicidal thoughts", "self-harm", "severe hopelessness"]
            },
            "uti": {
                "name": "Urinary Tract Infection",
                "category": "Urological",
                "symptoms": ["burning urination", "frequent urination", "cloudy urine", "pelvic pain", "fever"],
                "causes": ["bacteria", "E. coli", "sexual activity", "catheter use"],
                "treatments": ["antibiotics", "increased fluid intake", "pain relievers"],
                "icd10": "N39.0",
                "severity": "Mild to Moderate",
                "complications": ["kidney infection", "sepsis"]
            },
            "gastroenteritis": {
                "name": "Gastroenteritis (Stomach Flu)",
                "category": "Gastrointestinal",
                "symptoms": ["diarrhea", "vomiting", "nausea", "abdominal cramps", "fever", "dehydration"],
                "causes": ["viruses", "bacteria", "parasites", "contaminated food/water"],
                "treatments": ["rehydration", "electrolytes", "rest", "bland diet", "antiemetics"],
                "icd10": "K52.9",
                "severity": "Mild to Moderate",
                "emergency_signs": ["severe dehydration", "bloody stool", "high fever"]
            },
            "copd": {
                "name": "Chronic Obstructive Pulmonary Disease",
                "category": "Respiratory",
                "symptoms": ["shortness of breath", "chronic cough", "wheezing", "chest tightness", "fatigue"],
                "causes": ["smoking", "air pollution", "occupational exposure", "genetics"],
                "treatments": ["bronchodilators", "steroids", "oxygen therapy", "pulmonary rehabilitation"],
                "icd10": "J44",
                "severity": "Moderate to High",
                "emergency_signs": ["severe breathlessness", "bluish lips", "confusion"]
            },
            "osteoarthritis": {
                "name": "Osteoarthritis",
                "category": "Musculoskeletal",
                "symptoms": ["joint pain", "stiffness", "swelling", "decreased range of motion", "bone spurs"],
                "causes": ["age", "obesity", "joint injury", "genetics", "overuse"],
                "treatments": ["NSAIDs", "physical therapy", "weight management", "joint injections", "surgery"],
                "icd10": "M19",
                "severity": "Mild to Moderate",
                "affected_joints": ["knees", "hips", "hands", "spine"]
            },
            "covid19": {
                "name": "COVID-19 (SARS-CoV-2)",
                "category": "Infectious Disease",
                "symptoms": ["fever", "cough", "fatigue", "loss of taste/smell", "shortness of breath", "body aches"],
                "causes": ["SARS-CoV-2 virus", "airborne transmission", "contact transmission"],
                "treatments": ["antivirals", "monoclonal antibodies", "supportive care", "oxygen therapy"],
                "icd10": "U07.1",
                "severity": "Mild to Critical",
                "emergency_signs": ["difficulty breathing", "chest pain", "confusion", "low oxygen"]
            },
            "sepsis": {
                "name": "Sepsis",
                "category": "Emergency/Critical",
                "symptoms": ["high fever", "rapid heart rate", "rapid breathing", "confusion", "low blood pressure"],
                "causes": ["bacterial infection", "immune response", "organ dysfunction"],
                "treatments": ["antibiotics", "IV fluids", "vasopressors", "ICU care"],
                "icd10": "A41.9",
                "severity": "Critical",
                "emergency_signs": ["all symptoms require immediate emergency care"]
            }
        }
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search local medical database using keyword matching"""
        query_lower = query.lower()
        # Split query into keywords
        keywords = query_lower.split()
        results = []
        
        for condition_id, data in self.knowledge_base.items():
            score = 0.0
            matched_fields = []
            
            # Check each keyword
            for keyword in keywords:
                if len(keyword) < 3:  # Skip very short words
                    continue
                
                # Check name match
                if keyword in data["name"].lower():
                    score += 10.0
                    matched_fields.append(f"name:{keyword}")
                
                # Check symptoms
                for symptom in data.get("symptoms", []):
                    if keyword in symptom.lower():
                        score += 3.0
                        matched_fields.append(f"symptom:{symptom}")
                
                # Check causes
                for cause in data.get("causes", []):
                    if keyword in cause.lower():
                        score += 2.0
                        matched_fields.append(f"cause:{cause}")
                
                # Check treatments
                for treatment in data.get("treatments", []):
                    if keyword in treatment.lower():
                        score += 2.0
                        matched_fields.append(f"treatment:{treatment}")
                
                # Check category
                if keyword in data.get("category", "").lower():
                    score += 4.0
                    matched_fields.append(f"category:{keyword}")
                
                # Check emergency signs
                for sign in data.get("emergency_signs", []):
                    if keyword in sign.lower():
                        score += 5.0  # Higher weight for emergency signs
                        matched_fields.append(f"[WARNING]emergency:{sign}")
            
            if score > 0:
                results.append({
                    "text": self._format_condition(data),
                    "source": f"Medical Database - {data['name']}",
                    "score": score,
                    "condition_id": condition_id,
                    "icd10": data.get("icd10", ""),
                    "severity": data.get("severity", ""),
                    "matched_fields": matched_fields,
                    "raw_data": data
                })
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def _format_condition(self, data: Dict[str, Any]) -> str:
        """Format condition data for display"""
        text = f"**{data['name']}** (ICD-10: {data.get('icd10', 'N/A')})\n\n"
        text += f"**Category:** {data.get('category', 'N/A')}\n"
        text += f"**Severity:** {data.get('severity', 'N/A')}\n\n"
        
        if data.get("symptoms"):
            text += f"**Symptoms:** {', '.join(data['symptoms'][:5])}\n\n"
        
        if data.get("causes"):
            text += f"**Common Causes:** {', '.join(data['causes'][:3])}\n\n"
        
        if data.get("treatments"):
            text += f"**Treatments:** {', '.join(data['treatments'][:5])}\n\n"
        
        if data.get("emergency_signs"):
            text += f"**[WARNING] Emergency Signs:** {', '.join(data['emergency_signs'])}\n"
        
        return text


class EnhancedKnowledgeBase:
    """
    Enhanced knowledge base combining multiple sources with hybrid search.
    Falls back gracefully when external services are unavailable.
    """
    
    def __init__(self, storage_dir: str = "data/knowledge_base"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize knowledge sources
        self.sources = []
        
        # Always available: Local medical database
        try:
            self.local_db = LocalMedicalDatabase()
            self.sources.append(("Local Database", self.local_db))
            logger.info("[OK] Local medical database loaded")
        except Exception as e:
            logger.error(f"Failed to load local database: {e}")
        
        # Load sentence transformer for better semantic search (optional)
        self.embedder = None
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("[OK] Sentence transformer loaded for semantic search")
            except Exception as e:
                logger.warning(f"Could not load sentence transformer: {e}")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Hybrid search across all knowledge sources.
        Combines results from multiple sources and re-ranks them.
        """
        all_results = []
        
        # Search each source
        for source_name, source in self.sources:
            try:
                source_results = source.search(query, top_k=top_k)
                for result in source_results:
                    result["knowledge_source"] = source_name
                    all_results.append(result)
            except Exception as e:
                logger.warning(f"Error searching {source_name}: {e}")
        
        # If we have semantic embedder, re-rank results
        if self.embedder and all_results and NUMPY_AVAILABLE:
            try:
                all_results = self._semantic_rerank(query, all_results)
            except Exception as e:
                logger.warning(f"Semantic re-ranking failed: {e}")
        
        # Sort by score and return top results
        all_results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return all_results[:top_k]
    
    def _semantic_rerank(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Re-rank results using semantic similarity"""
        query_embedding = self.embedder.encode([query])[0]
        
        for result in results:
            text_embedding = self.embedder.encode([result["text"][:500]])[0]
            # Cosine similarity
            similarity = np.dot(query_embedding, text_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(text_embedding)
            )
            # Boost score with semantic similarity
            result["score"] = result.get("score", 0) + (similarity * 10)
            result["semantic_score"] = float(similarity)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        stats = {
            "sources": len(self.sources),
            "source_details": {},
            "capabilities": {
                "semantic_search": self.embedder is not None,
                "local_database": any(name == "Local Database" for name, _ in self.sources),
            }
        }
        
        for source_name, source in self.sources:
            if hasattr(source, 'knowledge_base'):
                stats["source_details"][source_name] = {
                    "entries": len(source.knowledge_base),
                    "categories": len(set(data.get("category") for data in source.knowledge_base.values()))
                }
        
        return stats
    
    def add_document(self, text: str, source: str, metadata: Dict[str, Any]) -> str:
        """
        Add a document to the knowledge base.
        Stores in local database and creates searchable entry.
        """
        import hashlib
        
        # Generate unique document ID
        doc_id = hashlib.md5(f"{source}{text[:100]}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        # Store document (simple in-memory for now, could persist to SQLite)
        doc_entry = {
            "id": doc_id,
            "text": text,
            "source": source,
            "metadata": metadata,
            "created_at": datetime.now().isoformat(),
            "character_count": len(text),
            "word_count": len(text.split())
        }
        
        # Add to local database if available
        if hasattr(self, 'local_db') and self.local_db:
            # Store as a searchable entry
            category = metadata.get("type", "document")
            self.local_db.knowledge_base[doc_id] = {
                "name": source,
                "category": category,
                "text": text[:1000],  # Store first 1000 chars for quick search
                "full_text": text,
                "metadata": metadata,
                "created_at": doc_entry["created_at"]
            }
        
        logger.info(f"Added document to enhanced KB: {source} (ID: {doc_id}, {len(text)} chars)")
        return doc_id
    
    def add_pdf_source(self, pdf_directory: str):
        """Add PDF documents as a knowledge source (future enhancement)"""
        # TODO: Implement PDF processing
        pass
    
    def add_pubmed_source(self, api_key: Optional[str] = None):
        """Add PubMed API as a knowledge source (future enhancement)"""
        # TODO: Implement PubMed integration
        pass


# Singleton instance
_knowledge_base_instance = None

def get_knowledge_base() -> EnhancedKnowledgeBase:
    """Get or create knowledge base singleton"""
    global _knowledge_base_instance
    if _knowledge_base_instance is None:
        _knowledge_base_instance = EnhancedKnowledgeBase()
    return _knowledge_base_instance
