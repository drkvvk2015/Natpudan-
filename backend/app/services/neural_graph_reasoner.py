"""
Neural Graph Reasoner (NGR)

Graph Neural Network-based reasoning engine for multi-hop inference
over medical knowledge graphs. Enables:
- Multi-hop question answering
- Path-based reasoning
- Contextual node embeddings
- Attention-weighted walks
- Temporal graph evolution
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class NodeEmbedding:
    """GNN-learned node representation"""
    node_id: str
    node_type: str
    features: np.ndarray
    context_embedding: np.ndarray  # Aggregated from neighbors
    attention_weights: Dict[str, float] = field(default_factory=dict)
    temporal_embeddings: List[Tuple[datetime, np.ndarray]] = field(default_factory=list)


@dataclass
class ReasoningPath:
    """A path through the graph for reasoning"""
    nodes: List[str]
    edges: List[Tuple[str, str, str]]  # (source, relation, target)
    confidence: float
    attention_score: float
    path_type: str  # direct, multi_hop, temporal


class GraphAttentionLayer:
    """
    Graph Attention Network (GAT) layer implementation.
    Learns attention weights between connected nodes.
    """

    def __init__(self, input_dim: int = 128, output_dim: int = 128, heads: int = 4):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.heads = heads
        self.head_dim = output_dim // heads

        # Initialize weights
        self.W = np.random.randn(input_dim, output_dim) * np.sqrt(2.0 / input_dim)
        self.a = np.random.randn(heads, 2 * self.head_dim) * np.sqrt(2.0 / (2 * self.head_dim))

    def forward(self, node_features: np.ndarray, adjacency: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Forward pass with multi-head attention.
        Returns: (output_features, attention_weights)
        """
        n_nodes = node_features.shape[0]

        # Linear transformation
        h = node_features @ self.W  # (n_nodes, output_dim)

        # Split into heads
        h_reshaped = h.reshape(n_nodes, self.heads, self.head_dim)

        # Calculate attention scores
        attention_scores = np.zeros((self.heads, n_nodes, n_nodes))

        for head in range(self.heads):
            for i in range(n_nodes):
                for j in range(n_nodes):
                    if adjacency[i, j] > 0:
                        # Concatenate features
                        concat = np.concatenate([h_reshaped[i, head], h_reshaped[j, head]])
                        # Attention score
                        attention_scores[head, i, j] = self.a[head] @ concat

        # Softmax normalization
        attention_weights = self._softmax(attention_scores, adjacency)

        # Apply attention
        out = np.zeros((n_nodes, self.heads, self.head_dim))
        for head in range(self.heads):
            out[:, head, :] = attention_weights[head] @ h_reshaped[:, head, :]

        # Concatenate heads
        output = out.reshape(n_nodes, self.output_dim)

        # ELU activation
        output = np.where(output > 0, output, np.exp(output) - 1)

        return output, attention_weights.mean(axis=0)  # Average across heads

    def _softmax(self, scores: np.ndarray, adjacency: np.ndarray) -> np.ndarray:
        """Masked softmax over neighbors"""
        result = np.zeros_like(scores)
        for head in range(self.heads):
            for i in range(scores.shape[1]):
                mask = adjacency[i] > 0
                if mask.sum() > 0:
                    masked_scores = scores[head, i, mask]
                    exp_scores = np.exp(masked_scores - masked_scores.max())
                    result[head, i, mask] = exp_scores / exp_scores.sum()
        return result


class GraphConvolutionLayer:
    """
    Graph Convolutional Network (GCN) layer.
    Aggregates neighbor information.
    """

    def __init__(self, input_dim: int = 128, output_dim: int = 128):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.W = np.random.randn(input_dim, output_dim) * np.sqrt(2.0 / input_dim)
        self.b = np.zeros(output_dim)

    def forward(self, features: np.ndarray, adjacency: np.ndarray) -> np.ndarray:
        """GCN forward pass"""
        # Degree normalization
        degree = adjacency.sum(axis=1, keepdims=True) + 1
        degree_inv_sqrt = np.power(degree, -0.5)
        degree_inv_sqrt[np.isinf(degree_inv_sqrt)] = 0

        # Normalized adjacency
        adj_norm = degree_inv_sqrt * adjacency * degree_inv_sqrt.T

        # Add self-loops
        adj_norm = adj_norm + np.eye(len(adjacency))

        # Message passing
        h = adj_norm @ features @ self.W + self.b

        # ReLU activation
        return np.maximum(h, 0)


class NeuralGraphReasoner:
    """
    Main Neural Graph Reasoning engine.
    Combines GNN layers with path-based reasoning.
    """

    def __init__(self, embedding_dim: int = 128, n_layers: int = 3):
        self.embedding_dim = embedding_dim
        self.n_layers = n_layers

        # GNN layers
        self.gcn_layers = [GraphConvolutionLayer(embedding_dim, embedding_dim)
                          for _ in range(n_layers)]
        self.gat_layer = GraphAttentionLayer(embedding_dim, embedding_dim, heads=4)

        # Graph storage
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Tuple[str, str, str]] = []  # (source, target, relation)
        self.adjacency: Optional[np.ndarray] = None
        self.node_embeddings: Dict[str, NodeEmbedding] = {}
        self.node_id_to_idx: Dict[str, int] = {}

        # Reasoning cache
        self.path_cache: Dict[str, List[ReasoningPath]] = {}

    def build_graph(self, nodes: List[Dict], edges: List[Tuple[str, str, str]]) -> None:
        """Build graph from nodes and edges"""
        self.nodes = {n["id"]: n for n in nodes}
        self.edges = edges

        # Build node index mapping
        self.node_id_to_idx = {node_id: i for i, node_id in enumerate(self.nodes.keys())}

        # Build adjacency matrix
        n = len(nodes)
        self.adjacency = np.zeros((n, n))

        for source_id, target_id, relation in edges:
            if source_id in self.node_id_to_idx and target_id in self.node_id_to_idx:
                i = self.node_id_to_idx[source_id]
                j = self.node_id_to_idx[target_id]
                self.adjacency[i, j] = 1.0

        # Initialize node features
        self._initialize_features()

        logger.info(f"[NGR] Graph built: {n} nodes, {len(edges)} edges")

    def _initialize_features(self) -> None:
        """Initialize node features with random embeddings"""
        for node_id, node_data in self.nodes.items():
            # Create feature vector based on node type and properties
            features = np.random.randn(self.embedding_dim)
            features = features / np.linalg.norm(features)

            embedding = NodeEmbedding(
                node_id=node_id,
                node_type=node_data.get("type", "unknown"),
                features=features,
                context_embedding=features.copy()
            )
            self.node_embeddings[node_id] = embedding

    def compute_embeddings(self) -> None:
        """Compute GNN node embeddings"""
        if self.adjacency is None or len(self.node_embeddings) == 0:
            return

        # Stack features into matrix
        node_ids = list(self.node_embeddings.keys())

        # Initial features
        features = np.stack([self.node_embeddings[nid].features for nid in node_ids])

        # GCN layers
        for i, layer in enumerate(self.gcn_layers):
            features = layer.forward(features, self.adjacency)

        # GAT layer for attention-weighted aggregation
        features, attention_weights = self.gat_layer.forward(features, self.adjacency)

        # Update embeddings
        for idx, node_id in enumerate(node_ids):
            embedding = self.node_embeddings[node_id]
            embedding.context_embedding = features[idx]

            # Extract attention weights for neighbors
            neighbor_weights = {}
            for neighbor_id, neighbor_idx in self.node_id_to_idx.items():
                if self.adjacency[idx, neighbor_idx] > 0:
                    neighbor_weights[neighbor_id] = float(attention_weights[idx, neighbor_idx])

            embedding.attention_weights = neighbor_weights

        logger.info("[NGR] Node embeddings computed")

    def reason_multi_hop(self, start_node: str, query_embedding: np.ndarray,
                        max_hops: int = 3, beam_width: int = 5) -> List[ReasoningPath]:
        """
        Multi-hop reasoning from start node using learned embeddings.
        """
        if start_node not in self.node_embeddings:
            return []

        if start_node in self.path_cache:
            return self.path_cache[start_node]

        paths = []
        start_embedding = self.node_embeddings[start_node].context_embedding

        # Beam search for reasoning paths
        beam = [(start_node, [start_node], [], 1.0)]  # (current, path_nodes, path_edges, score)

        for hop in range(max_hops):
            new_beam = []

            for current, path_nodes, path_edges, score in beam:
                if current not in self.node_id_to_idx:
                    continue

                current_idx = self.node_id_to_idx[current]

                # Find neighbors
                neighbors = []
                for neighbor_id, neighbor_idx in self.node_id_to_idx.items():
                    if self.adjacency[current_idx, neighbor_idx] > 0 and neighbor_id not in path_nodes:
                        # Get relation
                        relation = self._get_relation(current, neighbor_id)

                        # Calculate relevance score using embedding similarity
                        if neighbor_id in self.node_embeddings:
                            neighbor_emb = self.node_embeddings[neighbor_id].context_embedding
                            similarity = np.dot(start_embedding, neighbor_emb)
                            similarity = (similarity + 1) / 2  # Normalize to [0, 1]

                            # Combine with attention weight
                            attention = self.node_embeddings[current].attention_weights.get(neighbor_id, 0.5)
                            combined_score = score * (0.6 * similarity + 0.4 * attention)

                            neighbors.append((neighbor_id, relation, combined_score))

                # Sort and select top
                neighbors.sort(key=lambda x: x[2], reverse=True)
                selected = neighbors[:beam_width]

                for neighbor_id, relation, new_score in selected:
                    new_path_nodes = path_nodes + [neighbor_id]
                    new_path_edges = path_edges + [(current, relation, neighbor_id)]

                    if len(new_path_nodes) >= 2:
                        # Calculate path confidence
                        path_confidence = new_score * (1 - 0.1 * len(new_path_nodes))

                        # Calculate attention score
                        attention_score = np.mean([
                            self.node_embeddings[n].attention_weights.get(new_path_nodes[i+1], 0.5)
                            for i, n in enumerate(new_path_nodes[:-1])
                            if n in self.node_embeddings
                        ]) if len(new_path_nodes) > 1 else 0.5

                        path = ReasoningPath(
                            nodes=new_path_nodes,
                            edges=new_path_edges,
                            confidence=float(path_confidence),
                            attention_score=float(attention_score),
                            path_type="multi_hop" if len(new_path_nodes) > 2 else "direct"
                        )
                        paths.append(path)

                    new_beam.append((neighbor_id, new_path_nodes, new_path_edges, new_score))

            beam = sorted(new_beam, key=lambda x: x[3], reverse=True)[:beam_width * 2]

        # Sort paths by combined score
        paths.sort(key=lambda p: p.confidence * p.attention_score, reverse=True)

        # Cache results
        self.path_cache[start_node] = paths[:20]

        return paths[:20]

    def _get_relation(self, source: str, target: str) -> str:
        """Get relation type between two nodes"""
        for s, t, r in self.edges:
            if s == source and t == target:
                return r
        return "related_to"

    def answer_question(self, question: str, question_embedding: np.ndarray,
                       start_nodes: List[str]) -> Dict[str, Any]:
        """
        Answer medical question using graph reasoning.
        """
        all_paths = []
        relevant_nodes = set()

        for start_node in start_nodes:
            paths = self.reason_multi_hop(start_node, question_embedding, max_hops=3)
            all_paths.extend(paths)
            for path in paths[:5]:
                relevant_nodes.update(path.nodes)

        # Score paths against question
        scored_paths = []
        for path in all_paths:
            # Get path embedding (average of node embeddings)
            path_embeddings = [
                self.node_embeddings[n].context_embedding
                for n in path.nodes if n in self.node_embeddings
            ]

            if path_embeddings:
                path_embedding = np.mean(path_embeddings, axis=0)
                similarity = np.dot(question_embedding, path_embedding)

                final_score = (
                    path.confidence * 0.3 +
                    path.attention_score * 0.2 +
                    float(similarity) * 0.5
                )

                scored_paths.append((path, final_score))

        scored_paths.sort(key=lambda x: x[1], reverse=True)

        # Build answer
        top_paths = scored_paths[:5]
        answer_nodes = set()
        for path, _ in top_paths:
            answer_nodes.update(path.nodes)

        # Retrieve node information
        answer_content = []
        for node_id in answer_nodes:
            if node_id in self.nodes:
                node_info = self.nodes[node_id]
                answer_content.append({
                    "id": node_id,
                    "type": node_info.get("type", "unknown"),
                    "name": node_info.get("name", node_id),
                    "properties": {k: v for k, v in node_info.items()
                                  if k not in ["id", "type", "name"]}
                })

        return {
            "question": question,
            "reasoning_paths": [
                {
                    "nodes": path.nodes,
                    "edges": path.edges,
                    "confidence": path.confidence,
                    "attention": path.attention_score,
                    "path_type": path.path_type,
                    "relevance_score": float(score)
                }
                for path, score in top_paths
            ],
            "relevant_entities": answer_content,
            "nodes_explored": len(relevant_nodes),
            "reasoning_depth": max(len(p.nodes) for p, _ in top_paths) if top_paths else 0,
            "confidence": float(np.mean([score for _, score in top_paths])) if top_paths else 0
        }

    def find_path_between(self, source: str, target: str,
                         max_length: int = 5) -> Optional[ReasoningPath]:
        """Find reasoning path between two medical concepts"""
        if source not in self.node_embeddings or target not in self.node_embeddings:
            return None

        # BFS for shortest path
        queue = deque([(source, [source], [])])
        visited = {source}

        while queue:
            current, path_nodes, path_edges = queue.popleft()

            if current == target and len(path_nodes) > 1:
                return ReasoningPath(
                    nodes=path_nodes,
                    edges=path_edges,
                    confidence=1.0 / len(path_nodes),
                    attention_score=0.5,
                    path_type="path_between"
                )

            if len(path_nodes) >= max_length:
                continue

            if current not in self.node_id_to_idx:
                continue

            current_idx = self.node_id_to_idx[current]

            for neighbor_id in self.node_id_to_idx:
                if neighbor_id not in visited and self.adjacency[current_idx, self.node_id_to_idx[neighbor_id]] > 0:
                    visited.add(neighbor_id)
                    relation = self._get_relation(current, neighbor_id)
                    queue.append((
                        neighbor_id,
                        path_nodes + [neighbor_id],
                        path_edges + [(current, relation, neighbor_id)]
                    ))

        return None

    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get graph and reasoning statistics"""
        if not self.nodes:
            return {"status": "empty"}

        node_types = defaultdict(int)
        for node in self.nodes.values():
            node_types[node.get("type", "unknown")] += 1

        relation_types = defaultdict(int)
        for _, _, relation in self.edges:
            relation_types[relation] += 1

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": dict(node_types),
            "relation_types": dict(relation_types),
            "average_degree": len(self.edges) * 2 / len(self.nodes) if self.nodes else 0,
            "embedding_dim": self.embedding_dim,
            "gnn_layers": self.n_layers,
            "cached_paths": len(self.path_cache)
        }


# Singleton instance
_ngr_instance: Optional[NeuralGraphReasoner] = None


def get_neural_graph_reasoner() -> NeuralGraphReasoner:
    global _ngr_instance
    if _ngr_instance is None:
        _ngr_instance = NeuralGraphReasoner(embedding_dim=128, n_layers=3)
    return _ngr_instance
