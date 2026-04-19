"""
KB Growth Orchestrator
The "brain" that coordinates all auto-improvement subsystems:
- Seeds KB on first run
- Detects knowledge gaps from searches
- Periodically fetches online knowledge
- Learns from conversations
- Builds knowledge graph
- Reports growth metrics

This is the single entry point for the "growing child" KB system.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class KBGrowthOrchestrator:
    """
    Orchestrates the self-improving knowledge base system.

    Lifecycle:
    1. On startup: seed KB if first run
    2. On every search: record in gap detector
    3. On every AI response: optionally learn from conversation
    4. Periodically: fetch online knowledge for gaps
    5. Periodically: fetch latest research for core topics
    6. Continuous: quantum-inspired indexing, neural graph reasoning
    7. Predictive: anticipate gaps before they occur
    8. Autonomous: AI-driven research and synthesis
    """

    def __init__(self):
        self._initialized = False
        self._kb = None
        self._gap_detector = None
        self._ingester = None
        self._kg = None
        self._quantum_kb = None
        self._neural_reasoner = None
        self._predictive_detector = None
        self._research_agent = None
        self._metrics_history = []

    def initialize(self):
        """Initialize all subsystems (call once at startup)"""
        if self._initialized:
            return

        try:
            from app.services.local_vector_kb import get_local_knowledge_base
            self._kb = get_local_knowledge_base()
        except Exception as e:
            logger.error(f"[KB_GROWTH] Failed to get KB: {e}")
            return

        try:
            from app.services.kb_gap_detector import get_gap_detector
            self._gap_detector = get_gap_detector()
        except Exception as e:
            logger.warning(f"[KB_GROWTH] Gap detector init failed: {e}")

        try:
            from app.services.kb_auto_ingester import get_kb_ingester
            self._ingester = get_kb_ingester()
        except Exception as e:
            logger.warning(f"[KB_GROWTH] Ingester init failed: {e}")

        try:
            from app.services.knowledge_graph import get_knowledge_graph
            self._kg = get_knowledge_graph()
        except Exception as e:
            logger.warning(f"[KB_GROWTH] Knowledge graph init failed: {e}")

        # Initialize futuristic components
        try:
            from app.services.quantum_kb_engine import get_quantum_kb
            self._quantum_kb = get_quantum_kb()
            logger.info("[KB_GROWTH] Quantum KB engine initialized")
        except Exception as e:
            logger.warning(f"[KB_GROWTH] Quantum KB init failed: {e}")

        try:
            from app.services.neural_graph_reasoner import get_neural_graph_reasoner
            self._neural_reasoner = get_neural_graph_reasoner()
            logger.info("[KB_GROWTH] Neural graph reasoner initialized")
        except Exception as e:
            logger.warning(f"[KB_GROWTH] Neural reasoner init failed: {e}")

        try:
            from app.services.predictive_gap_detector import get_predictive_detector
            self._predictive_detector = get_predictive_detector()
            logger.info("[KB_GROWTH] Predictive gap detector initialized")
        except Exception as e:
            logger.warning(f"[KB_GROWTH] Predictive detector init failed: {e}")

        try:
            from app.services.autonomous_research_agent import get_research_agent
            self._research_agent = get_research_agent()
            logger.info("[KB_GROWTH] Autonomous research agent initialized")
        except Exception as e:
            logger.warning(f"[KB_GROWTH] Research agent init failed: {e}")

        self._initialized = True
        logger.info("[KB_GROWTH] Orchestrator initialized with futuristic capabilities")

    def seed_if_needed(self):
        """Run KB seeding on first launch"""
        if not self._kb:
            return

        try:
            from app.services.kb_auto_seeder import is_seeded, seed_knowledge_base
            if not is_seeded():
                logger.info("[KB_GROWTH] First run detected - seeding knowledge base...")
                stats = seed_knowledge_base(self._kb)
                logger.info(f"[KB_GROWTH] Seeding complete: {stats}")

                # Also build initial knowledge graph from seed data
                self._build_graph_from_seed()
            else:
                logger.info("[KB_GROWTH] KB already seeded")
        except Exception as e:
            logger.error(f"[KB_GROWTH] Seeding failed: {e}")

    def _build_graph_from_seed(self):
        """Build knowledge graph from seed data"""
        if not self._kg:
            return

        try:
            from app.services.kb_auto_seeder import MEDICAL_CONDITIONS, COMMON_MEDICATIONS

            for cond in MEDICAL_CONDITIONS:
                # Add condition node
                cond_id = cond["name"].lower().replace(" ", "_")
                self._kg.add_node(cond_id, "disease", cond["name"], {"icd10": cond["icd10"]})

                # Add symptom nodes and edges
                for symptom in cond.get("symptoms", [])[:5]:
                    sym_id = symptom.lower().replace(" ", "_").replace("(", "").replace(")", "")[:50]
                    self._kg.add_node(sym_id, "symptom", symptom)
                    self._kg.add_edge(cond_id, "has_symptom", sym_id)

                # Add treatment edges to medications
                for treatment in cond.get("treatments", [])[:3]:
                    treat_id = treatment.lower().replace(" ", "_")[:50]
                    self._kg.add_node(treat_id, "medication", treatment)
                    self._kg.add_edge(treat_id, "treats", cond_id)

            for med in COMMON_MEDICATIONS:
                med_id = med["name"].lower().replace(" ", "_")
                self._kg.add_node(med_id, "medication", med["name"], {"class": med["class"]})

                for indication in med.get("indications", []):
                    _ind_id = indication.lower().replace(" ", "_")[:50]  # noqa: F841
                    # Link if disease node exists
                    existing = self._kg.find_node(indication)
                    if existing:
                        self._kg.add_edge(med_id, "indicated_for", existing["id"])

            stats = self._kg.get_statistics()
            logger.info(f"[KB_GROWTH] Knowledge graph built: {stats.get('total_nodes', 0)} nodes, {stats.get('total_edges', 0)} edges")
        except Exception as e:
            logger.error(f"[KB_GROWTH] Graph building failed: {e}")

    def record_search(self, query: str, results: list, top_score: float = 0.0):
        """Record a search for gap detection (call from chat endpoint)"""
        if self._gap_detector:
            try:
                self._gap_detector.record_search(query, results, top_score)
            except Exception as e:
                logger.debug(f"[KB_GROWTH] Gap recording error: {e}")

        # Also record in predictive detector for trend analysis
        if self._predictive_detector:
            try:
                self._predictive_detector.record_query(query, len(results))
            except Exception as e:
                logger.debug(f"[KB_GROWTH] Predictive recording error: {e}")

    def learn_from_conversation(self, messages: list, patient_context: dict = None):
        """Learn from a completed conversation (call from chat endpoint)"""
        if self._ingester and self._kb:
            try:
                self._ingester.learn_from_conversation(self._kb, messages, patient_context)
            except Exception as e:
                logger.debug(f"[KB_GROWTH] Conversation learning error: {e}")

    async def periodic_online_fetch(self):
        """Fetch new knowledge from online sources (call periodically)"""
        if not self._ingester or not self._kb:
            return {"status": "not_initialized"}

        if not self._ingester.should_fetch_online(interval_hours=24):
            return {"status": "too_soon"}

        stats = {}

        # 1. Check predictive gaps first (futuristic)
        if self._predictive_detector:
            try:
                forecast = self._predictive_detector.predict_gaps(days_ahead=7)
                if forecast.critical_gaps:
                    critical_topics = [t.topic for t in forecast.critical_gaps[:3]]
                    logger.info(f"[KB_GROWTH] Predictive fill for: {critical_topics}")
                    # Prioritize these in gap filling
            except Exception as e:
                logger.debug(f"[KB_GROWTH] Predictive check error: {e}")

        # 2. Fill knowledge gaps (existing)
        if self._gap_detector:
            try:
                gap_result = await self._ingester.acquire_gap_knowledge(
                    kb=self._kb,
                    gap_detector=self._gap_detector,
                    max_topics=5,
                )
                stats["gap_acquisition"] = gap_result
            except Exception as e:
                logger.error(f"[KB_GROWTH] Gap acquisition failed: {e}")
                stats["gap_acquisition"] = {"error": str(e)}

        # 3. Fetch latest research for core topics
        try:
            from app.services.kb_auto_ingester import CORE_MEDICAL_TOPICS
            fetch_count = self._ingester.state.get("total_online_fetches", 0)
            start_idx = (fetch_count * 5) % len(CORE_MEDICAL_TOPICS)
            topics_batch = CORE_MEDICAL_TOPICS[start_idx:start_idx + 5]

            online_result = await self._ingester.fetch_online_knowledge(
                topics=topics_batch,
                kb=self._kb,
                max_per_topic=2,
            )
            stats["online_fetch"] = online_result
        except Exception as e:
            logger.error(f"[KB_GROWTH] Online fetch failed: {e}")
            stats["online_fetch"] = {"error": str(e)}

        # 4. Run autonomous research agent (futuristic)
        if self._research_agent:
            try:
                agent_result = await self._research_agent.run_cycle()
                stats["autonomous_agent"] = agent_result
            except Exception as e:
                logger.error(f"[KB_GROWTH] Autonomous agent error: {e}")
                stats["autonomous_agent"] = {"error": str(e)}

        return stats

    def get_growth_metrics(self) -> Dict[str, Any]:
        """Get comprehensive growth metrics for the KB system"""
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "kb": {},
            "gaps": {},
            "ingestion": {},
            "graph": {},
            "futuristic": {
                "quantum": {},
                "neural": {},
                "predictive": {},
                "autonomous": {}
            }
        }

        if self._kb:
            try:
                metrics["kb"] = self._kb.get_statistics()
            except Exception:
                pass

        if self._gap_detector:
            try:
                metrics["gaps"] = self._gap_detector.get_statistics()
            except Exception:
                pass

        if self._ingester:
            try:
                metrics["ingestion"] = self._ingester.get_statistics()
            except Exception:
                pass

        if self._kg:
            try:
                metrics["graph"] = self._kg.get_statistics()
            except Exception:
                pass

        # Futuristic components
        if self._quantum_kb:
            try:
                metrics["futuristic"]["quantum"] = self._quantum_kb.get_statistics()
            except Exception:
                pass

        if self._neural_reasoner:
            try:
                metrics["futuristic"]["neural"] = self._neural_reasoner.get_graph_statistics()
            except Exception:
                pass

        if self._predictive_detector:
            try:
                metrics["futuristic"]["predictive"] = self._predictive_detector.get_statistics()
            except Exception:
                pass

        if self._research_agent:
            try:
                metrics["futuristic"]["autonomous"] = self._research_agent.get_status()
            except Exception:
                pass

        # Store metrics history
        self._metrics_history.append(metrics)
        if len(self._metrics_history) > 100:
            self._metrics_history = self._metrics_history[-100:]

        return metrics


# Singleton
_orchestrator: Optional[KBGrowthOrchestrator] = None


def get_kb_orchestrator() -> KBGrowthOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = KBGrowthOrchestrator()
    return _orchestrator
