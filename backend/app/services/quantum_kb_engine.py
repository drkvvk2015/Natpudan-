"""
Quantum-Inspired Knowledge Base Engine

Uses probabilistic computing principles and holographic memory concepts
to create a resilient, high-dimensional knowledge representation system.

Features:
- Probabilistic retrieval with uncertainty quantification
- Holographic memory (distributed, redundant storage)
- Quantum-inspired superposition of concepts
- Multi-dimensional vector spaces
- Entanglement-inspired concept relationships
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict
import json
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class QuantumDocument:
    """Document in quantum-inspired representation"""
    id: str
    content: str
    amplitude_vector: np.ndarray  # Complex-valued vector
    phase_matrix: np.ndarray      # Phase relationships
    uncertainty: float            # Heisenberg-like uncertainty
    coherence: float              # Quantum coherence measure
    entangled_docs: Set[str]      # Entangled document IDs
    metadata: Dict[str, Any]
    created_at: datetime


@dataclass
class SuperpositionState:
    """Multiple concepts in superposition"""
    concepts: List[str]
    amplitudes: np.ndarray
    probabilities: np.ndarray
    collapsed: bool = False
    collapsed_to: Optional[str] = None


class HolographicMemory:
    """
    Holographic memory storage inspired by quantum holography principles.
    Information is distributed across the entire memory space, making it
    resilient to partial damage and enabling associative recall.
    """

    def __init__(self, dimension: int = 1024):
        self.dimension = dimension
        self.memory_space: np.ndarray = np.zeros(dimension, dtype=np.complex128)
        self.index_map: Dict[str, int] = {}
        self.pattern_library: Dict[str, np.ndarray] = {}

    def encode(self, key: str, pattern: np.ndarray, intensity: float = 1.0) -> None:
        """Encode pattern using holographic interference"""
        if len(pattern) != self.dimension:
            pattern = self._resize_pattern(pattern)

        # Create reference beam (key-based)
        reference = self._generate_reference_beam(key)

        # Interference pattern (hologram)
        hologram = pattern * reference * intensity

        # Store in distributed memory
        self.memory_space += hologram

        # Store reference pattern
        self.pattern_library[key] = pattern
        self.index_map[key] = len(self.index_map)

    def decode(self, key: str) -> Optional[np.ndarray]:
        """Decode pattern using reference beam reconstruction"""
        if key not in self.pattern_library:
            return None

        reference = self._generate_reference_beam(key)

        # Reconstruct through interference with conjugate reference
        reconstructed = self.memory_space * np.conj(reference)

        # Normalize
        reconstructed = reconstructed / (np.abs(reconstructed).max() + 1e-10)

        return np.real(reconstructed)

    def associative_recall(self, partial_pattern: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        """Recall similar patterns from partial input (associative memory)"""
        if len(partial_pattern) != self.dimension:
            partial_pattern = self._resize_pattern(partial_pattern)

        similarities = []
        for key, pattern in self.pattern_library.items():
            # Holographic similarity (interference pattern correlation)
            similarity = np.abs(np.vdot(partial_pattern, self.memory_space * np.conj(pattern)))
            similarity /= (np.linalg.norm(partial_pattern) * np.linalg.norm(pattern) + 1e-10)
            similarities.append((key, float(similarity)))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def _generate_reference_beam(self, key: str) -> np.ndarray:
        """Generate phase-reference beam from key"""
        np.random.seed(int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**32))
        phases = np.random.uniform(0, 2*np.pi, self.dimension)
        return np.exp(1j * phases)

    def _resize_pattern(self, pattern: np.ndarray) -> np.ndarray:
        """Resize pattern to match memory dimension using interpolation"""
        if len(pattern) < self.dimension:
            # Repeat and pad
            repeats = self.dimension // len(pattern) + 1
            resized = np.tile(pattern, repeats)[:self.dimension]
        else:
            # Downsample with averaging
            factor = len(pattern) // self.dimension
            resized = pattern[:self.dimension * factor].reshape(self.dimension, factor).mean(axis=1)

        # Normalize
        norm = np.linalg.norm(resized)
        if norm > 0:
            resized = resized / norm
        return resized.astype(np.complex128)


class QuantumInspiredSearch:
    """
    Search using quantum-inspired probabilistic methods.
    Implements Grover-like amplitude amplification and quantum walk concepts.
    """

    def __init__(self, vector_dim: int = 768):
        self.vector_dim = vector_dim
        self.documents: Dict[str, QuantumDocument] = {}
        self.entanglement_graph: Dict[str, Set[str]] = defaultdict(set)

    def add_document(self, doc_id: str, embedding: np.ndarray,
                   content: str, metadata: Dict[str, Any]) -> QuantumDocument:
        """Add document with quantum representation"""
        # Normalize to quantum state (unit vector)
        normalized = embedding / (np.linalg.norm(embedding) + 1e-10)

        # Create complex amplitude vector (quantum-inspired)
        amplitude = normalized.astype(np.complex128)
        amplitude = amplitude / np.linalg.norm(amplitude)

        # Phase matrix (represents concept relationships)
        phase_matrix = np.outer(np.angle(amplitude + 1e-10),
                                  np.angle(amplitude + 1e-10))

        # Calculate uncertainty (Heisenberg-inspired: position vs momentum)
        position_variance = np.var(np.abs(amplitude))
        momentum_variance = np.var(np.angle(amplitude))
        uncertainty = np.sqrt(position_variance * momentum_variance)

        # Calculate coherence (off-diagonal density matrix elements)
        density = np.outer(amplitude, np.conj(amplitude))
        coherence = np.sum(np.abs(density)) - np.sum(np.abs(np.diag(density)))
        coherence /= (self.vector_dim * (self.vector_dim - 1))

        doc = QuantumDocument(
            id=doc_id,
            content=content,
            amplitude_vector=amplitude,
            phase_matrix=phase_matrix,
            uncertainty=uncertainty,
            coherence=float(coherence),
            entangled_docs=set(),
            metadata=metadata,
            created_at=datetime.utcnow()
        )

        self.documents[doc_id] = doc

        # Auto-entangle similar documents
        self._auto_entangle(doc)

        return doc

    def _auto_entangle(self, new_doc: QuantumDocument, threshold: float = 0.85) -> None:
        """Automatically entangle highly similar documents"""
        for doc_id, doc in self.documents.items():
            if doc_id == new_doc.id:
                continue

            # Calculate quantum fidelity
            fidelity = np.abs(np.vdot(new_doc.amplitude_vector, doc.amplitude_vector))**2

            if fidelity > threshold:
                new_doc.entangled_docs.add(doc_id)
                doc.entangled_docs.add(new_doc.id)
                self.entanglement_graph[new_doc.id].add(doc_id)
                self.entanglement_graph[doc_id].add(new_doc.id)

    def probabilistic_search(self, query_embedding: np.ndarray,
                           top_k: int = 10,
                           uncertainty_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Search with quantum-inspired probability distributions.
        Returns results with probability scores and uncertainty measures.
        """
        # Normalize query
        query = query_embedding / (np.linalg.norm(query_embedding) + 1e-10)
        query = query.astype(np.complex128)

        results = []

        for doc_id, doc in self.documents.items():
            # Calculate probability amplitude ( Born rule: |<ψ|φ>|² )
            amplitude = np.vdot(query, doc.amplitude_vector)
            probability = np.abs(amplitude) ** 2

            # Include uncertainty in scoring
            confidence = 1.0 - min(doc.uncertainty / uncertainty_threshold, 1.0)
            adjusted_score = probability * confidence

            # Consider entangled documents (quantum context)
            entanglement_boost = 0.0
            if doc.entangled_docs:
                entangled_scores = []
                for entangled_id in doc.entangled_docs:
                    if entangled_id in self.documents:
                        ent_doc = self.documents[entangled_id]
                        ent_amp = np.vdot(query, ent_doc.amplitude_vector)
                        entangled_scores.append(np.abs(ent_amp) ** 2)

                if entangled_scores:
                    entanglement_boost = np.mean(entangled_scores) * 0.1

            final_score = adjusted_score + entanglement_boost

            results.append({
                "id": doc_id,
                "content": doc.content[:500],
                "probability": float(probability),
                "adjusted_score": float(final_score),
                "uncertainty": float(doc.uncertainty),
                "coherence": float(doc.coherence),
                "entangled_count": len(doc.entangled_docs),
                "metadata": doc.metadata,
                "confidence": float(confidence)
            })

        # Sort by adjusted score
        results.sort(key=lambda x: x["adjusted_score"], reverse=True)
        return results[:top_k]

    def superposition_query(self, concepts: List[str],
                           embeddings: Dict[str, np.ndarray]) -> SuperpositionState:
        """
        Put multiple concepts in superposition and collapse to most relevant.
        """
        if not concepts:
            return SuperpositionState(concepts=[], amplitudes=np.array([]), probabilities=np.array([]))

        # Create superposition
        amplitudes = []
        valid_concepts = []

        for concept in concepts:
            if concept in embeddings:
                emb = embeddings[concept]
                normalized = emb / (np.linalg.norm(emb) + 1e-10)
                amplitudes.append(normalized)
                valid_concepts.append(concept)

        if not amplitudes:
            return SuperpositionState(concepts=[], amplitudes=np.array([]), probabilities=np.array([]))

        # Superposition amplitudes (equal weights)
        superposition = np.mean(amplitudes, axis=0)
        superposition = superposition / np.linalg.norm(superposition)

        # Calculate probabilities for each concept
        probs = []
        for amp in amplitudes:
            prob = np.abs(np.vdot(superposition, amp.astype(np.complex128))) ** 2
            probs.append(float(prob))

        probs = np.array(probs)
        probs = probs / probs.sum()  # Normalize

        return SuperpositionState(
            concepts=valid_concepts,
            amplitudes=superposition,
            probabilities=probs,
            collapsed=False
        )

    def collapse_superposition(self, state: SuperpositionState,
                              measurement_basis: np.ndarray) -> SuperpositionState:
        """
        Collapse superposition to a definite state based on measurement.
        """
        if state.collapsed:
            return state

        # Measurement in given basis
        basis = measurement_basis / (np.linalg.norm(measurement_basis) + 1e-10)
        basis = basis.astype(np.complex128)

        # Calculate projection probabilities
        probabilities = []
        for i, concept in enumerate(state.concepts):
            # Find document for this concept
            for doc_id, doc in self.documents.items():
                if concept in doc.content:
                    prob = np.abs(np.vdot(basis, doc.amplitude_vector)) ** 2
                    probabilities.append((i, concept, prob))
                    break

        if not probabilities:
            return state

        # Collapse to most probable
        probabilities.sort(key=lambda x: x[2], reverse=True)
        collapsed_idx, collapsed_concept, _ = probabilities[0]

        return SuperpositionState(
            concepts=state.concepts,
            amplitudes=state.amplitudes,
            probabilities=state.probabilities,
            collapsed=True,
            collapsed_to=collapsed_concept
        )


class QuantumKBEngine:
    """
    Main Quantum-Inspired Knowledge Base Engine.
    Combines holographic memory and quantum search.
    """

    def __init__(self, dimension: int = 1024):
        self.holographic = HolographicMemory(dimension=dimension)
        self.quantum_search = QuantumInspiredSearch(vector_dim=dimension)
        self.embeddings_cache: Dict[str, np.ndarray] = {}
        self.query_history: List[Dict[str, Any]] = []

    def index_document(self, doc_id: str, content: str,
                      embedding: np.ndarray, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Index a document using quantum-inspired methods"""
        # Add to holographic memory
        self.holographic.encode(doc_id, embedding)

        # Add to quantum search
        qdoc = self.quantum_search.add_document(doc_id, embedding, content, metadata)

        # Cache embedding
        self.embeddings_cache[doc_id] = embedding

        return {
            "id": doc_id,
            "uncertainty": qdoc.uncertainty,
            "coherence": qdoc.coherence,
            "entangled_documents": list(qdoc.entangled_docs),
            "indexed": True
        }

    def search(self, query_embedding: np.ndarray, query_text: str,
               top_k: int = 10, use_holographic: bool = True) -> Dict[str, Any]:
        """
        Search with quantum-inspired probabilistic results.
        """
        start_time = datetime.utcnow()

        # Quantum probabilistic search
        quantum_results = self.quantum_search.probabilistic_search(
            query_embedding, top_k=top_k
        )

        # Holographic associative recall (if enabled)
        holographic_results = []
        if use_holographic:
            holographic_results = self.holographic.associative_recall(
                query_embedding, top_k=top_k
            )

        # Combine results
        combined_scores: Dict[str, float] = {}

        for result in quantum_results:
            combined_scores[result["id"]] = combined_scores.get(result["id"], 0) + result["adjusted_score"]

        for key, score in holographic_results:
            combined_scores[key] = combined_scores.get(key, 0) + score * 0.5

        # Sort by combined score
        sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

        # Build final results
        final_results = []
        for doc_id, score in sorted_results[:top_k]:
            if doc_id in self.quantum_search.documents:
                doc = self.quantum_search.documents[doc_id]
                final_results.append({
                    "id": doc_id,
                    "content": doc.content[:1000],
                    "score": float(score),
                    "metadata": doc.metadata,
                    "quantum_properties": {
                        "uncertainty": doc.uncertainty,
                        "coherence": doc.coherence,
                        "entangled_with": list(doc.entangled_docs)
                    }
                })

        search_time = (datetime.utcnow() - start_time).total_seconds()

        # Record query
        self.query_history.append({
            "query": query_text[:200],
            "timestamp": datetime.utcnow().isoformat(),
            "results_count": len(final_results),
            "search_time_ms": search_time * 1000
        })

        return {
            "results": final_results,
            "total_found": len(combined_scores),
            "search_time_ms": search_time * 1000,
            "method": "quantum_inspired",
            "holographic_used": use_holographic
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics"""
        total_docs = len(self.quantum_search.documents)
        avg_uncertainty = np.mean([d.uncertainty for d in self.quantum_search.documents.values()]) if total_docs > 0 else 0
        avg_coherence = np.mean([d.coherence for d in self.quantum_search.documents.values()]) if total_docs > 0 else 0

        entanglement_count = sum(len(d.entangled_docs) for d in self.quantum_search.documents.values())

        return {
            "total_documents": total_docs,
            "holographic_memory_size": self.holographic.dimension,
            "average_uncertainty": float(avg_uncertainty),
            "average_coherence": float(avg_coherence),
            "entanglement_pairs": entanglement_count // 2,
            "queries_served": len(self.query_history),
            "memory_utilization": len(self.holographic.pattern_library) / self.holographic.dimension
        }


# Singleton instance
_quantum_kb: Optional[QuantumKBEngine] = None


def get_quantum_kb() -> QuantumKBEngine:
    global _quantum_kb
    if _quantum_kb is None:
        _quantum_kb = QuantumKBEngine(dimension=1024)
    return _quantum_kb
