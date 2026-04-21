"""
Medical Core API Router - Diagnosis and Clinical Analysis
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List, Dict, Any, Optional
import logging
import os
import tempfile

from app.services.icd10_service import get_icd10_service
from app.services.vector_knowledge_base import get_vector_knowledge_base
from app.services.ai_treatment_recommender import get_treatment_recommender
from app.services.pdf_processor import pdf_processor
from app.services.hybrid_search import get_hybrid_search
from app.services.rag_service import get_rag_service
from app.services.medical_entity_extractor import get_entity_extractor
from app.services.pubmed_integration import get_pubmed_integration
from app.services.knowledge_graph import get_knowledge_graph

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/medical", tags=["medical"])

@router.post("/diagnosis")
def diagnosis(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generate diagnosis suggestions from symptoms"""
    symptoms: List[str] = payload.get("symptoms", [])
    try:
        if not symptoms:
            return {
                "error": "No symptoms provided",
                "primary_diagnosis": "Unknown",
                "differential_diagnoses": [],
                "suggested_icd_codes": []
            }

        icd_service = get_icd10_service()
        suggested_codes = icd_service.suggest_codes(symptoms)

        primary_diagnosis = "Undetermined"
        if suggested_codes:
            primary_diagnosis = suggested_codes[0].get("description", "Undetermined")

        differential_diagnoses = [
            code.get("description", "")
            for code in suggested_codes[1:5]
        ]

        return {
            "primary_diagnosis": primary_diagnosis,
            "differential_diagnoses": differential_diagnoses,
            "symptoms": symptoms,
            "suggested_icd_codes": suggested_codes[:5]
        }
    except Exception as e:
        logger.error(f"Error generating diagnosis: {e}")
        return {
            "error": str(e),
            "primary_diagnosis": "Error",
            "differential_diagnoses": [],
            "symptoms": symptoms
        }

@router.post("/analyze-symptoms")
def analyze_symptoms(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze symptoms and suggest related conditions"""
    symptoms: List[Any] = payload.get("symptoms", [])
    try:
        if not symptoms:
            return {"error": "No symptoms provided", "analysis": []}

        icd_service = get_icd10_service()
        analysis: List[Dict[str, Any]] = []

        for symptom in symptoms:
            codes = icd_service.search_codes(symptom, max_results=3)
            analysis.append({
                "symptom": symptom,
                "related_conditions": codes
            })

        return {
            "symptoms": symptoms,
            "analysis": analysis,
            "count": len(analysis)
        }
    except Exception as e:
        logger.error(f"Error analyzing symptoms: {e}")
        return {"error": str(e), "symptoms": symptoms, "analysis": []}


@router.post("/live-diagnosis")
def live_diagnosis(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generate diagnosis suggestions from richer clinical context."""
    try:
        complaints = payload.get("complaints", [])
        patient_history = payload.get("patient_history", "")
        vital_signs = payload.get("vital_signs", {})
        anthropometry = payload.get("anthropometry", {})
        clinical_findings = payload.get("clinical_findings", [])

        if not complaints:
            return {
                "differential_diagnoses": [],
                "recommended_tests": [],
                "clinical_summary": "No complaints provided",
                "data_completeness": 0.0,
            }

        symptoms: List[str] = []
        for complaint in complaints:
            if isinstance(complaint, dict):
                value = str(complaint.get("complaint", "")).strip()
            else:
                value = str(complaint).strip()
            if value:
                symptoms.append(value)

        supporting_evidence: List[str] = []
        for finding in clinical_findings:
            if not isinstance(finding, dict):
                supporting_evidence.append(str(finding))
                continue
            system = str(finding.get("system", "")).strip()
            detail = str(finding.get("finding", "")).strip()
            normalized = f"{system}: {detail}" if system and detail else detail or system
            if normalized:
                supporting_evidence.append(normalized)

        data_completeness = 0.2
        if patient_history:
            data_completeness += 0.2
        if vital_signs:
            data_completeness += 0.2
        if anthropometry:
            data_completeness += 0.1
        if clinical_findings:
            data_completeness += 0.3

        icd_service = get_icd10_service()
        suggested_codes = icd_service.suggest_codes(symptoms)

        differential_diagnoses: List[Dict[str, Any]] = []
        for idx, code in enumerate(suggested_codes[:5]):
            confidence = max(0.3, 0.9 - (idx * 0.15))
            differential_diagnoses.append(
                {
                    "diagnosis": code.get("description", "Unknown"),
                    "disease_name": code.get("description", "Unknown"),
                    "confidence": confidence,
                    "icd_code": code.get("code", ""),
                    "supporting_evidence": supporting_evidence[:3] if supporting_evidence else symptoms[:2],
                }
            )

        search_space = [item.lower() for item in [*symptoms, *supporting_evidence]]
        recommended_tests: List[str] = []
        if any("chest pain" in item or "heart" in item for item in search_space):
            recommended_tests.extend(["ECG", "Troponins", "Chest X-ray"])
        if any("fever" in item or "infection" in item for item in search_space):
            recommended_tests.extend(["CBC", "Blood cultures", "CRP"])
        if any("abdominal" in item or "stomach" in item for item in search_space):
            recommended_tests.extend(["Abdominal ultrasound", "Lipase", "Liver function tests"])
        if any("headache" in item or "neuro" in item for item in search_space):
            recommended_tests.extend(["CT head", "MRI brain"])
        recommended_tests = list(dict.fromkeys(recommended_tests))

        primary_complaint = symptoms[0] if symptoms else "Unknown complaint"
        duration_info = ""
        if complaints and isinstance(complaints[0], dict) and complaints[0].get("duration"):
            duration_info = f" for {complaints[0]['duration']}"

        clinical_summary = f"Patient presents with {primary_complaint}{duration_info}. "
        if len(symptoms) > 1:
            clinical_summary += f"Associated symptoms include {', '.join(symptoms[1:3])}. "
        if patient_history:
            clinical_summary += "Comprehensive history available. "
        if supporting_evidence:
            clinical_summary += f"Positive findings on exam: {', '.join(supporting_evidence[:5])}. "
        clinical_summary += f"Data completeness: {int(data_completeness * 100)}%."

        return {
            "differential_diagnoses": differential_diagnoses,
            "recommended_tests": recommended_tests,
            "clinical_summary": clinical_summary,
            "data_completeness": data_completeness,
        }
    except Exception as e:
        logger.error(f"Error in live diagnosis: {e}")
        return {
            "error": str(e),
            "differential_diagnoses": [],
            "recommended_tests": [],
            "clinical_summary": "Error processing request",
            "data_completeness": 0.0,
        }


@router.post("/live-diagnosis/suggest-treatment")
def suggest_treatment(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Compatibility endpoint for the diagnosis screen."""
    diagnosis = payload.get("diagnosis", "")
    patient_data = {
        "age": payload.get("patient_age"),
        "gender": payload.get("patient_gender"),
        "comorbidities": payload.get("comorbidities", []),
    }
    recommender = get_treatment_recommender()
    return recommender.recommend_treatment(diagnosis, patient_data)


@router.post("/parse-medical-report")
async def parse_medical_report(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Extract structured data from uploaded PDF reports."""
    suffix = os.path.splitext(file.filename or "report.pdf")[1] or ".pdf"
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(await file.read())
            temp_path = temp_file.name

        report_data = pdf_processor.process_report(temp_path)
        flattened_lab_results: List[Dict[str, Any]] = []
        for category_results in report_data.get("lab_results", {}).values():
            if not isinstance(category_results, dict):
                continue
            for test_name, value in category_results.items():
                flattened_lab_results.append({"test": test_name, "value": str(value)})

        diagnoses = [
            {
                "description": item.get("description", ""),
                "icd10_code": item.get("code") if item.get("code") not in (None, "Unknown") else None,
            }
            for item in report_data.get("diagnoses", [])
        ]

        return {
            "vitals": report_data.get("vitals", {}),
            "medications": report_data.get("medications", []),
            "lab_results": flattened_lab_results,
            "diagnoses": diagnoses,
            "allergies": report_data.get("allergies", []),
        }
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)

@router.get("/icd/search")
def icd_search(query: str, max_results: int = 20) -> List[Dict[str, str]]:
    """Search ICD-10 codes by code or description"""
    try:
        if not query:
            return []

        icd_service = get_icd10_service()
        results = icd_service.search_codes(query, max_results=max_results)

        return results
    except Exception as e:
        logger.error(f"Error searching ICD codes: {e}")
        return [{"error": str(e)}]

@router.get("/icd/code/{code}")
def icd_get_code(code: str) -> Dict[str, Any]:
    """Get specific ICD-10 code details"""
    try:
        icd_service = get_icd10_service()
        result = icd_service.get_code(code)

        if result is None:
            return {"error": "Code not found", "code": code}

        return result
    except Exception as e:
        logger.error(f"Error getting ICD code: {e}")
        return {"error": str(e), "code": code}

@router.get("/icd/categories")
def icd_categories() -> List[str]:
    """Get all ICD-10 categories"""
    try:
        icd_service = get_icd10_service()
        return icd_service.get_categories()
    except Exception as e:
        logger.error(f"Error getting ICD categories: {e}")
        return []

# ---- FUTURISTIC KNOWLEDGE BASE ENDPOINTS ----

@router.post("/knowledge/hybrid-search")
def hybrid_search(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    HYBRID SEARCH: Combines vector similarity + BM25 keyword matching
    """
    query: str = payload.get("query", "")
    try:
        top_k = payload.get("top_k", 10)
        alpha = payload.get("alpha", 0.5)

        kb = get_vector_knowledge_base()
        vector_results = kb.search(query, top_k=top_k * 2)

        hybrid_search_engine = get_hybrid_search()
        results = hybrid_search_engine.hybrid_search(
            query=query,
            vector_results=vector_results,
            top_k=top_k,
            alpha=alpha
        )

        return {
            "query": query,
            "results": results,
            "count": len(results),
            "search_type": "hybrid",
            "alpha": alpha
        }
    except Exception as e:
        logger.error(f"Error in hybrid search: {e}")
        return {"error": str(e), "query": query, "results": []}

@router.post("/knowledge/rag-query")
def rag_query(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    RAG: Retrieval-Augmented Generation
    """
    query: str = payload.get("query", "")
    try:
        max_context = payload.get("max_context_chunks", 5)

        kb = get_vector_knowledge_base()
        retrieved_docs = kb.search(query, top_k=max_context)

        rag_service = get_rag_service()
        response = rag_service.generate_with_context(
            query=query,
            retrieved_docs=retrieved_docs,
            include_citations=True
        )

        return response
    except Exception as e:
        logger.error(f"Error in RAG query: {e}")
        return {"error": str(e), "query": query}


@router.post("/knowledge/extract-entities")
def extract_medical_entities(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    ENTITY EXTRACTION: Automatically extract diseases, medications, procedures
    """
    try:
        text = payload.get("text", "")
        include_summary = payload.get("include_summary", True)

        extractor = get_entity_extractor()
        entities = extractor.extract_entities(text)
        icd_codes = extractor.extract_icd_codes(text)
        dosages = extractor.extract_dosages(text)

        result = {
            "entities": entities,
            "icd_codes": icd_codes,
            "dosages": dosages
        }

        if include_summary:
            summary = extractor.build_medical_summary(entities)
            result["summary"] = summary

        return result
    except Exception as e:
        logger.error(f"Error extracting entities: {e}")
        return {"error": str(e)}

@router.get("/knowledge/pubmed-latest")
def pubmed_latest_research(
    topic: str = "diabetes",
    max_results: int = 5,
    days_back: int = 30
) -> Dict[str, Any]:
    """
    PUBMED INTEGRATION: Fetch latest medical research
    """
    try:
        pubmed = get_pubmed_integration()
        papers = pubmed.search_papers(
            query=topic,
            max_results=max_results,
            days_back=days_back,
            sort="date"
        )

        return {
            "topic": topic,
            "papers": papers,
            "count": len(papers),
            "days_back": days_back
        }
    except Exception as e:
        logger.error(f"Error fetching PubMed research: {e}")
        return {"error": str(e), "topic": topic, "papers": []}

@router.post("/knowledge/pubmed-auto-update")
def pubmed_auto_update(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    AUTO-UPDATE: Automatically index latest PubMed research
    """
    try:
        topics = payload.get("topics", ["diabetes", "hypertension", "cancer"])
        papers_per_topic = payload.get("papers_per_topic", 3)
        days_back = payload.get("days_back", 7)

        pubmed = get_pubmed_integration()
        kb = get_vector_knowledge_base()

        result: Dict[str, Any] = pubmed.auto_update_knowledge_base(
            vector_kb=kb,
            topics=topics,
            papers_per_topic=papers_per_topic,
            days_back=days_back
        )

        return result
    except Exception as e:
        logger.error(f"Error auto-updating from PubMed: {e}")
        return {"error": str(e)}

@router.get("/knowledge/graph/visualize")
def visualize_knowledge_graph(
    concept: str = "diabetes",
    max_distance: int = 1
) -> Dict[str, Any]:
    """
    KNOWLEDGE GRAPH: Visualize medical concept relationships
    """
    try:
        kg = get_knowledge_graph()

        node = kg.find_node(concept)
        if not node:
            return {"error": f"Concept '{concept}' not found in knowledge graph"}

        visualization = kg.visualize_subgraph(
            center_node_id=node["id"],
            max_distance=max_distance
        )
        stats = kg.get_statistics()

        return {
            "concept": concept,
            "visualization": visualization,
            "statistics": stats,
            "node": node
        }
    except Exception as e:
        logger.error(f"Error visualizing knowledge graph: {e}")
        return {"error": str(e), "concept": concept}

@router.post("/knowledge/graph/build-from-text")
def build_graph_from_text(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    GRAPH BUILDER: Build knowledge graph from medical text
    """
    try:
        text = payload.get("text", "")

        extractor = get_entity_extractor()
        entities = extractor.extract_entities(text)

        kg = get_knowledge_graph()
        kg.build_from_entities(entities)
        stats = kg.get_statistics()

        return {
            "message": "Knowledge graph built successfully",
            "statistics": stats,
            "entities_extracted": {
                "diseases": len(entities.get("diseases", [])),
                "medications": len(entities.get("medications", [])),
                "symptoms": len(entities.get("symptoms", []))
            }
        }
    except Exception as e:
        logger.error(f"Error building knowledge graph: {e}")
        return {"error": str(e)}

@router.get("/knowledge/graph/export")
def export_knowledge_graph() -> Dict[str, Any]:
    """
    GRAPH EXPORT: Export entire knowledge graph as JSON
    """
    try:
        kg = get_knowledge_graph()
        graph_data = kg.export_graph()
        return graph_data
    except Exception as e:
        logger.error(f"Error exporting knowledge graph: {e}")
        return {"error": str(e)}
