"""
Futuristic KB API Endpoints

Exposes quantum-inspired search, neural graph reasoning,
predictive gap detection, and autonomous agent capabilities.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Tuple, cast
from datetime import datetime, timezone
import logging
import hashlib

import numpy as np

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/futuristic-kb", tags=["futuristic-kb"])


class QuantumSearchRequest(BaseModel):
    query: str
    top_k: int = 10
    use_holographic: bool = True


class ReasoningRequest(BaseModel):
    question: str
    start_concepts: List[str]
    max_hops: int = 3


class PathBetweenRequest(BaseModel):
    source_concept: str
    target_concept: str


def _deterministic_embedding(text: str, dimension: int = 384) -> List[float]:
    """Create a deterministic local embedding fallback from text."""
    if dimension <= 0:
        return []

    values: List[float] = []
    seed = text.encode("utf-8")

    while len(values) < dimension:
        seed = hashlib.sha256(seed).digest()
        for byte in seed:
            values.append((byte / 127.5) - 1.0)
            if len(values) >= dimension:
                break

    norm = float(np.linalg.norm(values))
    if norm > 0:
        values = [v / norm for v in values]

    return values


def _resize_embedding(values: List[float], target_dim: int) -> List[float]:
    """Resize embedding to target dimension using interpolation/truncation."""
    if target_dim <= 0:
        return values
    if not values:
        return [0.0] * target_dim
    if len(values) == target_dim:
        return values

    src = np.asarray(values, dtype=np.float32)
    src_x = np.linspace(0.0, 1.0, num=len(src), endpoint=True)
    dst_x = np.linspace(0.0, 1.0, num=target_dim, endpoint=True)
    resized = np.interp(dst_x, src_x, src)
    norm = float(np.linalg.norm(resized))
    if norm > 0:
        resized = resized / norm
    return resized.astype(np.float32).tolist()


async def _generate_embedding(text: str, dimension: int = 384) -> List[float]:
    """Generate embedding via local model when available; fallback deterministically."""
    try:
        from app.services.local_vector_kb import get_local_knowledge_base

        kb = get_local_knowledge_base()
        ensure_model_loaded = getattr(kb, "_ensure_model_loaded", None)
        if callable(ensure_model_loaded):
            ensure_model_loaded()

        model = getattr(kb, "embedding_model", None)
        if model is not None:
            embedding = model.encode([text], convert_to_numpy=True)[0]
            vector = embedding.astype(np.float32).tolist()
            return _resize_embedding(vector, dimension)
    except Exception as exc:
        logger.warning("[FUTURISTIC] Local embedding generation failed, using fallback: %s", exc)

    return _deterministic_embedding(text, dimension=dimension)


@router.post("/quantum-search")
async def quantum_search(request: QuantumSearchRequest) -> Dict[str, Any]:
    """
    Search using quantum-inspired probabilistic methods.
    Returns results with uncertainty measures and quantum properties.
    """
    try:
        from app.services.quantum_kb_engine import get_quantum_kb

        # Perform quantum search
        qkb = get_quantum_kb()
        target_dim = int(getattr(getattr(qkb, "holographic", None), "dimension", 1024))

        # Get query embedding
        query_embedding = np.asarray(
            await _generate_embedding(request.query, dimension=target_dim),
            dtype=np.float32,
        )

        results = qkb.search(
            query_embedding=query_embedding,
            query_text=request.query,
            top_k=request.top_k,
            use_holographic=request.use_holographic
        )

        return {
            "method": "quantum_inspired",
            "query": request.query,
            **results
        }

    except Exception as e:
        logger.error(f"[FUTURISTIC] Quantum search error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/quantum-stats")
async def quantum_stats() -> Dict[str, Any]:
    """Get quantum KB engine statistics"""
    try:
        from app.services.quantum_kb_engine import get_quantum_kb
        qkb = get_quantum_kb()
        return qkb.get_statistics()
    except Exception as e:
        logger.error(f"[FUTURISTIC] Quantum stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/neural-reasoning")
async def neural_reasoning(request: ReasoningRequest) -> Dict[str, Any]:
    """
    Multi-hop neural graph reasoning for complex medical questions.
    Uses GNN attention weights for explainable inference.
    """
    try:
        from app.services.neural_graph_reasoner import get_neural_graph_reasoner
        from app.services.knowledge_graph import get_knowledge_graph

        # Build graph if needed
        ngr = get_neural_graph_reasoner()
        kg = get_knowledge_graph()

        target_dim = int(getattr(ngr, "embedding_dim", 128))

        # Get embeddings for concepts
        query_embedding = np.asarray(
            await _generate_embedding(request.question, dimension=target_dim),
            dtype=np.float32,
        )

        # Convert knowledge graph to neural format
        graph_payload = kg.export_graph()
        raw_nodes = cast(List[Dict[str, Any]], graph_payload.get("nodes", []))
        raw_edges = cast(List[Dict[str, Any]], graph_payload.get("edges", []))

        nodes: List[Dict[str, Any]] = [
            {
                "id": str(node.get("id", "")),
                "type": str(node.get("type", "unknown")),
                "name": str(node.get("label", node.get("id", "unknown"))),
            }
            for node in raw_nodes
            if node.get("id")
        ]

        edges: List[Tuple[str, str, str]] = [
            (
                str(edge.get("source", "")),
                str(edge.get("target", "")),
                str(edge.get("relation", "related")),
            )
            for edge in raw_edges
            if edge.get("source") and edge.get("target")
        ]

        if len(ngr.nodes) == 0 and nodes:
            ngr_any: Any = ngr
            ngr_any.build_graph(nodes, edges)
            ngr_any.compute_embeddings()

        # Answer question
        answer = ngr.answer_question(
            question=request.question,
            question_embedding=query_embedding,
            start_nodes=request.start_concepts
        )

        return {
            "method": "neural_graph_reasoning",
            "gnn_layers": ngr.n_layers,
            **answer
        }

    except Exception as e:
        logger.error(f"[FUTURISTIC] Neural reasoning error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/find-path")
async def find_concept_path(request: PathBetweenRequest) -> Dict[str, Any]:
    """Find reasoning path between two medical concepts"""
    try:
        from app.services.neural_graph_reasoner import get_neural_graph_reasoner
        ngr = get_neural_graph_reasoner()

        path = ngr.find_path_between(
            source=request.source_concept,
            target=request.target_concept
        )

        if path is None:
            return {
                "found": False,
                "message": f"No path found between {request.source_concept} and {request.target_concept}"
            }

        return {
            "found": True,
            "source": request.source_concept,
            "target": request.target_concept,
            "path": {
                "nodes": path.nodes,
                "edges": path.edges,
                "confidence": path.confidence,
                "path_type": path.path_type
            }
        }

    except Exception as e:
        logger.error(f"[FUTURISTIC] Find path error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/neural-graph-stats")
async def neural_graph_stats() -> Dict[str, Any]:
    """Get neural graph statistics"""
    try:
        from app.services.neural_graph_reasoner import get_neural_graph_reasoner
        ngr = get_neural_graph_reasoner()
        return ngr.get_graph_statistics()
    except Exception as e:
        logger.error(f"[FUTURISTIC] Neural graph stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/predictive-forecast")
async def predictive_forecast(days_ahead: int = 14) -> Dict[str, Any]:
    """
    Get predictive forecast for upcoming knowledge gaps.
    """
    try:
        from app.services.predictive_gap_detector import get_predictive_detector

        detector = get_predictive_detector()
        forecast = detector.predict_gaps(days_ahead=days_ahead)

        return {
            "forecast_timestamp": forecast.timestamp.isoformat(),
            "emerging_topics": [
                {
                    "topic": t.topic,
                    "current_demand": t.current_demand,
                    "predicted_demand": t.predicted_demand,
                    "trend": t.trend_direction,
                    "confidence": t.confidence,
                    "urgency": t.urgency_score,
                    "action": t.recommended_action
                }
                for t in forecast.emerging_topics
            ],
            "critical_gaps": [
                {
                    "topic": t.topic,
                    "urgency": t.urgency_score,
                    "predicted_peak": t.predicted_peak_date.isoformat() if t.predicted_peak_date else None,
                    "action": t.recommended_action
                }
                for t in forecast.critical_gaps
            ],
            "seasonal_patterns": forecast.seasonal_patterns
        }

    except Exception as e:
        logger.error(f"[FUTURISTIC] Predictive forecast error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/agent/trigger-cycle")
async def trigger_agent_cycle(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Manually trigger the autonomous research agent cycle.
    """
    try:
        from app.services.autonomous_research_agent import get_research_agent

        agent = get_research_agent()

        # Run in background
        background_tasks.add_task(agent.run_cycle)

        return {
            "status": "started",
            "message": "Autonomous research cycle triggered",
            "agent_status": agent.get_status()
        }

    except Exception as e:
        logger.error(f"[FUTURISTIC] Agent trigger error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/agent/status")
async def get_agent_status() -> Dict[str, Any]:
    """Get autonomous agent status"""
    try:
        from app.services.autonomous_research_agent import get_research_agent
        agent = get_research_agent()
        return agent.get_status()
    except Exception as e:
        logger.error(f"[FUTURISTIC] Agent status error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/comprehensive-status")
async def get_comprehensive_status() -> Dict[str, Any]:
    """
    Get comprehensive status of all futuristic KB components.
    """
    try:
        status: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": {}
        }

        # Quantum KB
        try:
            from app.services.quantum_kb_engine import get_quantum_kb
            status["components"]["quantum_kb"] = get_quantum_kb().get_statistics()
        except Exception as e:
            status["components"]["quantum_kb"] = {"error": str(e)}

        # Neural Graph
        try:
            from app.services.neural_graph_reasoner import get_neural_graph_reasoner
            status["components"]["neural_graph"] = get_neural_graph_reasoner().get_graph_statistics()
        except Exception as e:
            status["components"]["neural_graph"] = {"error": str(e)}

        # Predictive Detector
        try:
            from app.services.predictive_gap_detector import get_predictive_detector
            status["components"]["predictive"] = get_predictive_detector().get_statistics()
        except Exception as e:
            status["components"]["predictive"] = {"error": str(e)}

        # Autonomous Agent
        try:
            from app.services.autonomous_research_agent import get_research_agent
            status["components"]["autonomous_agent"] = get_research_agent().get_status()
        except Exception as e:
            status["components"]["autonomous_agent"] = {"error": str(e)}

        return status

    except Exception as e:
        logger.error(f"[FUTURISTIC] Comprehensive status error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/index-document")
async def index_document_futuristic(content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Index a document using all futuristic methods simultaneously.
    """
    try:
        from app.services.quantum_kb_engine import get_quantum_kb
        from app.services.local_vector_kb import get_local_knowledge_base

        doc_id = content.get("id", f"doc_{datetime.now(timezone.utc).timestamp()}")
        text = content.get("text", "")
        metadata = content.get("metadata", {})

        qkb = get_quantum_kb()
        target_dim = int(getattr(getattr(qkb, "holographic", None), "dimension", 1024))

        # Generate embedding
        embedding = np.asarray(
            await _generate_embedding(text, dimension=target_dim),
            dtype=np.float32,
        )

        # Index in quantum KB
        quantum_result = qkb.index_document(
            doc_id=doc_id,
            content=text,
            embedding=embedding,
            metadata=metadata
        )

        # Index in traditional KB
        kb = get_local_knowledge_base()
        chunks = kb.add_document(
            content=text,
            metadata={**metadata, "futuristic_indexed": True}
        )

        return {
            "success": True,
            "doc_id": doc_id,
            "quantum_properties": quantum_result,
            "traditional_chunks": chunks,
            "methods": ["quantum", "traditional"]
        }

    except Exception as e:
        logger.error(f"[FUTURISTIC] Index document error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
