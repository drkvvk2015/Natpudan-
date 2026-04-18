"""
Medical Knowledge Graph Service
Creates semantic connections between medical concepts
"""

import logging
from typing import List, Dict, Any, Set, Optional, Tuple
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


class MedicalKnowledgeGraph:
    """
    Knowledge graph for medical concepts.
    Tracks relationships between diseases, symptoms, medications, procedures.
    """
    
    def __init__(self):
        """Initialize knowledge graph"""
        # Node storage: node_id -> {type, label, properties}
        self.nodes = {}
        
        # Edge storage: (source, relation, target)
        self.edges = []
        
        # Indexes for fast lookup
        self.node_by_label = defaultdict(list)
        self.edges_by_source = defaultdict(list)
        self.edges_by_target = defaultdict(list)
        
        logger.info("Medical knowledge graph initialized")
    
    def add_node(
        self,
        node_id: str,
        node_type: str,
        label: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add node to knowledge graph.
        
        Args:
            node_id: Unique identifier
            node_type: Type (disease, symptom, medication, procedure)
            label: Human-readable label
            properties: Additional properties
            
        Returns:
            Node ID
        """
        if node_id in self.nodes:
            # Update existing node
            self.nodes[node_id].update({
                "type": node_type,
                "label": label,
                "properties": properties or {}
            })
        else:
            # Create new node
            self.nodes[node_id] = {
                "id": node_id,
                "type": node_type,
                "label": label,
                "properties": properties or {}
            }
            self.node_by_label[label.lower()].append(node_id)
        
        return node_id
    
    def add_edge(
        self,
        source_id: str,
        relation: str,
        target_id: str,
        properties: Optional[Dict[str, Any]] = None
    ):
        """
        Add relationship between nodes.
        
        Args:
            source_id: Source node ID
            relation: Relationship type (causes, treats, symptom_of, etc.)
            target_id: Target node ID
            properties: Edge properties (strength, confidence, etc.)
        """
        # Verify nodes exist
        if source_id not in self.nodes or target_id not in self.nodes:
            logger.warning(f"Cannot add edge: node not found")
            return
        
        edge = {
            "source": source_id,
            "relation": relation,
            "target": target_id,
            "properties": properties or {}
        }
        
        self.edges.append(edge)
        self.edges_by_source[source_id].append(edge)
        self.edges_by_target[target_id].append(edge)
    
    def find_node(self, label: str) -> Optional[Dict[str, Any]]:
        """Find node by label"""
        node_ids = self.node_by_label.get(label.lower(), [])
        if node_ids:
            return self.nodes[node_ids[0]]
        return None
    
    def get_neighbors(
        self,
        node_id: str,
        relation: Optional[str] = None,
        direction: str = "out"
    ) -> List[Dict[str, Any]]:
        """
        Get neighboring nodes.
        
        Args:
            node_id: Node to get neighbors for
            relation: Filter by relationship type
            direction: "out" (outgoing), "in" (incoming), or "both"
            
        Returns:
            List of neighbor nodes
        """
        neighbors = []
        
        # Outgoing edges
        if direction in ("out", "both"):
            for edge in self.edges_by_source.get(node_id, []):
                if relation is None or edge["relation"] == relation:
                    target = self.nodes[edge["target"]]
                    neighbors.append({
                        **target,
                        "relation": edge["relation"],
                        "edge_properties": edge.get("properties", {})
                    })
        
        # Incoming edges
        if direction in ("in", "both"):
            for edge in self.edges_by_target.get(node_id, []):
                if relation is None or edge["relation"] == relation:
                    source = self.nodes[edge["source"]]
                    neighbors.append({
                        **source,
                        "relation": edge["relation"],
                        "edge_properties": edge.get("properties", {})
                    })
        
        return neighbors
    
    def find_path(
        self,
        start_id: str,
        end_id: str,
        max_depth: int = 3
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Find path between two nodes using BFS.
        
        Args:
            start_id: Starting node
            end_id: Target node
            max_depth: Maximum path length
            
        Returns:
            Path as list of nodes, or None if no path
        """
        if start_id not in self.nodes or end_id not in self.nodes:
            return None
        
        # BFS
        queue = [(start_id, [start_id])]
        visited = {start_id}
        
        while queue:
            current_id, path = queue.pop(0)
            
            if len(path) > max_depth:
                continue
            
            if current_id == end_id:
                # Found path
                return [self.nodes[nid] for nid in path]
            
            # Explore neighbors
            for edge in self.edges_by_source.get(current_id, []):
                neighbor_id = edge["target"]
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, path + [neighbor_id]))
        
        return None
    
    def get_related_concepts(
        self,
        node_id: str,
        max_distance: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Get all concepts related to a node within distance.
        
        Args:
            node_id: Source node
            max_distance: Maximum relationship distance
            
        Returns:
            List of related nodes with distances
        """
        if node_id not in self.nodes:
            return []
        
        # BFS to find all nodes within distance
        related = []
        queue = [(node_id, 0)]
        visited = {node_id}
        
        while queue:
            current_id, distance = queue.pop(0)
            
            if distance > max_distance:
                continue
            
            if distance > 0:
                node = self.nodes[current_id].copy()
                node["distance"] = distance
                related.append(node)
            
            # Explore neighbors
            neighbors = self.get_neighbors(current_id, direction="both")
            for neighbor in neighbors:
                neighbor_id = neighbor["id"]
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, distance + 1))
        
        return related
    
    def build_from_entities(
        self,
        extracted_entities: Dict[str, List[Dict[str, Any]]]
    ):
        """
        Build knowledge graph from extracted medical entities.
        
        Args:
            extracted_entities: Entities from medical_entity_extractor
        """
        # Add nodes
        disease_nodes = []
        medication_nodes = []
        symptom_nodes = []
        
        # Diseases
        for disease in extracted_entities.get("diseases", []):
            node_id = f"disease_{disease['entity']}"
            self.add_node(
                node_id=node_id,
                node_type="disease",
                label=disease['entity'],
                properties={"frequency": disease['count']}
            )
            disease_nodes.append(node_id)
        
        # Medications
        for med in extracted_entities.get("medications", []):
            node_id = f"medication_{med['entity']}"
            self.add_node(
                node_id=node_id,
                node_type="medication",
                label=med['entity'],
                properties={"frequency": med['count']}
            )
            medication_nodes.append(node_id)
        
        # Symptoms
        for symptom in extracted_entities.get("symptoms", []):
            node_id = f"symptom_{symptom['entity']}"
            self.add_node(
                node_id=node_id,
                node_type="symptom",
                label=symptom['entity'],
                properties={"frequency": symptom['count']}
            )
            symptom_nodes.append(node_id)
        
        # Create relationships (co-occurrence based)
        # Symptoms -> Diseases
        for symptom_id in symptom_nodes:
            for disease_id in disease_nodes:
                self.add_edge(
                    source_id=symptom_id,
                    relation="may_indicate",
                    target_id=disease_id,
                    properties={"confidence": 0.5}
                )
        
        # Medications -> Diseases (treatment)
        for med_id in medication_nodes:
            for disease_id in disease_nodes:
                self.add_edge(
                    source_id=med_id,
                    relation="treats",
                    target_id=disease_id,
                    properties={"confidence": 0.6}
                )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics"""
        node_types = defaultdict(int)
        for node in self.nodes.values():
            node_types[node["type"]] += 1
        
        relation_types = defaultdict(int)
        for edge in self.edges:
            relation_types[edge["relation"]] += 1
        
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": dict(node_types),
            "relation_types": dict(relation_types)
        }
    
    def export_graph(self) -> Dict[str, Any]:
        """Export graph as JSON"""
        return {
            "nodes": list(self.nodes.values()),
            "edges": self.edges,
            "statistics": self.get_statistics()
        }
    
    def visualize_subgraph(
        self,
        center_node_id: str,
        max_distance: int = 1
    ) -> str:
        """
        Generate simple text visualization of subgraph.

        Args:
            center_node_id: Center node
            max_distance: Distance from center

        Returns:
            Text representation
        """
        if center_node_id not in self.nodes:
            return "Node not found"

        center = self.nodes[center_node_id]
        lines = [
            f"Knowledge Graph around: {center['label']} ({center['type']})",
            "=" * 60,
            ""
        ]

        # Get related concepts
        related = self.get_related_concepts(center_node_id, max_distance)

        # Group by type
        by_type = defaultdict(list)
        for node in related:
            by_type[node["type"]].append(node)

        # Display by type
        for node_type, nodes in by_type.items():
            lines.append(f"{node_type.upper()}:")
            for node in nodes[:10]:  # Limit display
                distance = node.get("distance", 0)
                lines.append(f"  {'  ' * distance}→ {node['label']}")
            lines.append("")

        return "\n".join(lines)

    def get_subgraph(
        self,
        node_id: str,
        max_distance: int = 2
    ) -> Dict[str, Any]:
        """
        Get subgraph centered on a node with max distance.

        Args:
            node_id: Center node ID
            max_distance: Maximum distance from center

        Returns:
            {
                center: node,
                nodes: [nodes in subgraph],
                edges: [edges in subgraph],
                statistics: {...}
            }
        """
        if node_id not in self.nodes:
            return {
                "error": "Node not found",
                "node_id": node_id,
                "nodes": [],
                "edges": []
            }

        center_node = self.nodes[node_id]

        # Find all nodes within distance
        visited = {node_id}
        queue = [(node_id, 0)]
        subgraph_nodes = {node_id: center_node}

        while queue:
            current_id, distance = queue.pop(0)

            if distance >= max_distance:
                continue

            # Explore neighbors
            neighbors = self.get_neighbors(current_id, direction="both")
            for neighbor in neighbors:
                neighbor_id = neighbor["id"]
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    subgraph_nodes[neighbor_id] = neighbor
                    queue.append((neighbor_id, distance + 1))

        # Find edges within subgraph
        subgraph_edges = []
        for edge in self.edges:
            if edge["source"] in subgraph_nodes and edge["target"] in subgraph_nodes:
                subgraph_edges.append(edge)

        # Calculate statistics
        node_types = defaultdict(int)
        for node in subgraph_nodes.values():
            node_types[node["type"]] += 1

        relation_types = defaultdict(int)
        for edge in subgraph_edges:
            relation_types[edge["relation"]] += 1

        return {
            "center": center_node,
            "nodes": list(subgraph_nodes.values()),
            "edges": subgraph_edges,
            "statistics": {
                "total_nodes": len(subgraph_nodes),
                "total_edges": len(subgraph_edges),
                "node_types": dict(node_types),
                "relation_types": dict(relation_types),
                "max_distance": max_distance
            }
        }

    def export_for_d3(
        self,
        node_id: Optional[str] = None,
        max_distance: int = 2
    ) -> Dict[str, Any]:
        """
        Export graph in D3.js-compatible format (nodes/links).

        Args:
            node_id: Optional center node for subgraph (None = full graph)
            max_distance: Distance for subgraph export

        Returns:
            {
                nodes: [{id, label, type, size, color}],
                links: [{source, target, relation, value}]
            }
        """
        # Get subgraph or full graph
        if node_id and node_id in self.nodes:
            subgraph_data = self.get_subgraph(node_id, max_distance)
            nodes = subgraph_data.get("nodes", [])
            edges = subgraph_data.get("edges", [])
        else:
            nodes = list(self.nodes.values())
            edges = self.edges

        # Convert to D3 format
        d3_nodes = []
        node_id_map = {}  # Map internal IDs to D3 indices

        for i, node in enumerate(nodes):
            node_id_map[node["id"]] = i

            # Assign color based on node type
            color_map = {
                "disease": "#FF6B6B",
                "medication": "#4ECDC4",
                "symptom": "#FFE66D",
                "procedure": "#95E1D3",
                "default": "#A8E6CF"
            }

            color = color_map.get(node.get("type", "default"), color_map["default"])

            # Size based on frequency/connections
            connections = len(self.edges_by_source.get(node["id"], [])) + \
                         len(self.edges_by_target.get(node["id"], []))
            size = 10 + (connections * 2)  # Base size + connections

            d3_nodes.append({
                "id": node["id"],
                "label": node.get("label", node["id"]),
                "type": node.get("type", "unknown"),
                "size": size,
                "color": color,
                "properties": node.get("properties", {})
            })

        # Convert edges to D3 links
        d3_links = []
        for edge in edges:
            source_idx = node_id_map.get(edge["source"])
            target_idx = node_id_map.get(edge["target"])

            if source_idx is not None and target_idx is not None:
                d3_links.append({
                    "source": source_idx,
                    "target": target_idx,
                    "relation": edge.get("relation", "related"),
                    "value": edge.get("properties", {}).get("strength", 1),
                    "properties": edge.get("properties", {})
                })

        return {
            "nodes": d3_nodes,
            "links": d3_links,
            "statistics": {
                "total_nodes": len(d3_nodes),
                "total_links": len(d3_links),
                "node_types": {
                    nt: sum(1 for n in d3_nodes if n["type"] == nt)
                    for nt in set(n["type"] for n in d3_nodes)
                }
            }
        }


# Global instance
_knowledge_graph = None

def get_knowledge_graph() -> MedicalKnowledgeGraph:
    """Get or create knowledge graph instance"""
    global _knowledge_graph
    if _knowledge_graph is None:
        _knowledge_graph = MedicalKnowledgeGraph()
    return _knowledge_graph
