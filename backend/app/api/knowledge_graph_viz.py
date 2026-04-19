"""Knowledge Graph Visualization API"""
from fastapi import APIRouter, HTTPException
from app.services.knowledge_graph import get_knowledge_graph
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/knowledge-graph", tags=["knowledge-graph-viz"])

@router.get("/export/d3")
def export_for_d3(node_id: str = None, max_distance: int = 2):
    """Export knowledge graph in D3.js format"""
    try:
        kg = get_knowledge_graph()
        graph_data = kg.export_graph()
        
        if node_id:
            subgraph = kg.get_subgraph(node_id, max_distance)
            graph_data = subgraph
        
        nodes = []
        links = []
        node_colors = {"disease": "#FF6B6B", "medication": "#4ECDC4", "symptom": "#FFE66D", "procedure": "#95E1D3"}
        
        for node in graph_data.get("nodes", []):
            nodes.append({
                "id": node.get("id", ""),
                "label": node.get("label", ""),
                "type": node.get("type", "unknown"),
                "color": node_colors.get(node.get("type", "unknown"), "#999"),
                "size": len(node.get("edges", [])) * 5 + 10
            })
        
        for edge in graph_data.get("edges", []):
            links.append({"source": edge[0], "target": edge[1], "weight": 1})
        
        return {"nodes": nodes, "links": links}
    except Exception as e:
        logger.error(f"[KG_VIZ] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.get("/subgraph/{node_id}")
def get_subgraph(node_id: str, max_distance: int = 2):
    """Get subgraph centered on a node"""
    try:
        kg = get_knowledge_graph()
        subgraph = kg.get_subgraph(node_id, max_distance)

        # Return node info for detail dialog
        return {
            "id": node_id,
            "label": subgraph.get("center_label", node_id),
            "type": subgraph.get("center_type", "unknown"),
            "related_nodes": subgraph.get("neighbors", []),
            "description": subgraph.get("description", "")
        }
    except Exception as e:
        logger.error(f"[KG_VIZ] Subgraph error: {e}")
        return {
            "id": node_id,
            "label": node_id,
            "type": "unknown",
            "related_nodes": [],
            "description": ""
        }

@router.get("/search")
def search_graph(query: str, limit: int = 20):
    """Search knowledge graph and return D3 format"""
    try:
        kg = get_knowledge_graph()
        results = kg.search(query, limit)

        # Convert to D3 format
        nodes = []
        links = []
        node_colors = {"disease": "#FF6B6B", "medication": "#4ECDC4", "symptom": "#FFE66D", "procedure": "#95E1D3"}

        for item in results if isinstance(results, list) else []:
            node_id = item.get("id", str(len(nodes)))
            nodes.append({
                "id": node_id,
                "label": item.get("label", item.get("text", "")),
                "type": item.get("type", "unknown"),
                "color": node_colors.get(item.get("type", "unknown"), "#999"),
                "size": 20
            })

        return {"nodes": nodes, "links": links, "query": query}
    except Exception as e:
        logger.error(f"[KG_VIZ] Search error: {e}")
        return {"nodes": [], "links": [], "query": query}

@router.get("/stats")
def get_graph_stats():
    """Get knowledge graph statistics"""
    kg = get_knowledge_graph()
    return kg.get_statistics()
