"""
Knowledge Base Auto-Ingestion Pipeline
Fetches medical knowledge from online sources (PubMed, CDC, WHO)
and indexes it into the local vector KB.
Also learns from doctor-patient conversations.
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class KBAutoIngester:
    """
    Automatic knowledge ingestion pipeline.

    Sources:
    1. Online medical databases (PubMed, CDC, WHO, NIH)
    2. Doctor-patient conversation transcripts
    3. Gap-driven acquisition (topics users ask about but KB can't answer)

    The "growing child" concept:
    - Starts with seed knowledge (kb_auto_seeder)
    - Learns from every interaction (gap detection)
    - Periodically fetches new knowledge from online sources
    - Extracts knowledge from conversations
    - Builds persistent knowledge graph relationships
    """

    def __init__(self, storage_dir: str = "data/knowledge_base"):
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.state_path = os.path.join(backend_dir, storage_dir, "ingestion_state.json")
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "last_online_fetch": None,
            "last_gap_acquisition": None,
            "total_documents_ingested": 0,
            "total_online_fetches": 0,
            "topics_covered": [],
            "fetch_history": [],
        }

    def _save_state(self):
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
        try:
            with open(self.state_path, "w") as f:
                json.dump(self.state, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"[KB_INGEST] Failed to save state: {e}")

    async def fetch_online_knowledge(
        self,
        topics: List[str],
        kb,
        sources: List[str] = None,
        max_per_topic: int = 3,
    ) -> Dict[str, Any]:
        """
        Fetch knowledge from online medical sources and index into KB.

        Args:
            topics: Medical topics to search
            kb: LocalVectorKnowledgeBase instance
            sources: Which sources to use (default: all available)
            max_per_topic: Max documents per topic

        Returns:
            Stats dict with counts
        """
        stats = {"topics_searched": 0, "documents_found": 0, "documents_indexed": 0, "errors": []}

        try:
            from app.services.online_medical_sources import get_online_medical_sources
            online = get_online_medical_sources()
        except ImportError:
            try:
                from app.services.pubmed_integration import get_pubmed_integration
                online = get_pubmed_integration()
            except ImportError:
                logger.warning("[KB_INGEST] No online source modules available")
                return {**stats, "error": "No online source modules available"}

        for topic in topics:
            try:
                logger.info(f"[KB_INGEST] Fetching online knowledge for: {topic}")
                stats["topics_searched"] += 1

                # Use the auto_update method if available
                if hasattr(online, 'auto_update_knowledge_base'):
                    result = None
                    if asyncio.iscoroutinefunction(online.auto_update_knowledge_base):
                        result = await online.auto_update_knowledge_base(
                            vector_kb=kb,
                            topics=[topic],
                            results_per_topic=max_per_topic if hasattr(online, 'fetch_comprehensive_knowledge') else 3,
                        )
                    else:
                        result = online.auto_update_knowledge_base(
                            vector_kb=kb,
                            topics=[topic],
                            papers_per_topic=max_per_topic,
                            days_back=30,
                        )

                    if result:
                        found = result.get("documents_found", result.get("papers_found", 0))
                        indexed = result.get("documents_indexed", result.get("papers_indexed", 0))
                        stats["documents_found"] += found
                        stats["documents_indexed"] += indexed

                elif hasattr(online, 'fetch_comprehensive_knowledge'):
                    # Manual fetch and index
                    results = await online.fetch_comprehensive_knowledge(
                        query=topic, max_results=max_per_topic
                    )
                    for source_name, docs in results.items():
                        for doc in docs:
                            try:
                                formatted = online.format_for_indexing(doc)
                                chunks = kb.add_document(  # noqa: F841
                                    content=formatted["content"],
                                    metadata={
                                        **formatted.get("metadata", {}),
                                        "source": f"Online - {source_name}",
                                        "ingested_at": datetime.utcnow().isoformat(),
                                        "topic": topic,
                                    },
                                    chunk_size=1500,
                                    chunk_overlap=100,
                                )
                                stats["documents_found"] += 1
                                stats["documents_indexed"] += 1
                            except Exception as e:
                                logger.error(f"[KB_INGEST] Index error: {e}")

                elif hasattr(online, 'search_papers'):
                    # PubMed integration fallback
                    papers = online.search_papers(query=topic, max_results=max_per_topic, days_back=30)
                    for paper in papers:
                        try:
                            formatted = online.format_paper_for_indexing(paper)
                            _chunks = kb.add_document(  # noqa: F841
                                content=formatted["content"],
                                metadata={
                                    **formatted.get("metadata", {}),
                                    "ingested_at": datetime.utcnow().isoformat(),
                                    "topic": topic,
                                },
                                chunk_size=1500,
                                chunk_overlap=100,
                            )
                            stats["documents_found"] += 1
                            stats["documents_indexed"] += 1
                        except Exception as e:
                            logger.error(f"[KB_INGEST] Paper index error: {e}")

            except Exception as e:
                error_msg = f"Topic '{topic}': {str(e)[:200]}"
                stats["errors"].append(error_msg)
                logger.error(f"[KB_INGEST] {error_msg}")

        # Update state
        self.state["last_online_fetch"] = datetime.utcnow().isoformat()
        self.state["total_documents_ingested"] += stats["documents_indexed"]
        self.state["total_online_fetches"] += 1
        for topic in topics:
            if topic not in self.state["topics_covered"]:
                self.state["topics_covered"].append(topic)
        self.state["fetch_history"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "topics": topics,
            "indexed": stats["documents_indexed"],
        })
        # Keep last 100 fetch history entries
        self.state["fetch_history"] = self.state["fetch_history"][-100:]
        self._save_state()

        logger.info(f"[KB_INGEST] Online fetch complete: {stats}")
        return stats

    async def acquire_gap_knowledge(self, kb, gap_detector, max_topics: int = 5) -> Dict[str, Any]:
        """
        Fetch knowledge for detected gaps - topics users asked about
        but KB couldn't answer well.

        Args:
            kb: LocalVectorKnowledgeBase instance
            gap_detector: KnowledgeGapDetector instance
            max_topics: Max gaps to fill per run
        """
        topics = gap_detector.get_acquisition_topics(limit=max_topics)
        if not topics:
            logger.info("[KB_INGEST] No knowledge gaps to fill")
            return {"status": "no_gaps", "topics": []}

        logger.info(f"[KB_INGEST] Filling {len(topics)} knowledge gaps: {topics}")
        result = await self.fetch_online_knowledge(topics=topics, kb=kb, max_per_topic=3)

        # Mark resolved gaps
        for topic in topics:
            if result.get("documents_indexed", 0) > 0:
                gap_detector.mark_resolved(topic)

        self.state["last_gap_acquisition"] = datetime.utcnow().isoformat()
        self._save_state()

        return {**result, "gap_topics": topics}

    def learn_from_conversation(
        self,
        kb,
        conversation_messages: List[Dict[str, str]],
        patient_context: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Extract medical knowledge from doctor-patient conversations
        and add to KB.

        Args:
            kb: LocalVectorKnowledgeBase instance
            conversation_messages: List of {role, content} messages
            patient_context: Optional patient info for context
        """
        stats = {"extracted": 0, "indexed": 0}

        # Only learn from conversations with medical content
        medical_keywords = {
            "diagnosis", "treatment", "medication", "symptom", "prescribed",
            "condition", "disease", "therapy", "surgery", "lab results",
            "blood pressure", "heart rate", "dosage", "side effect",
            "prognosis", "referral", "follow-up", "imaging", "biopsy",
        }

        # Combine messages into conversation text
        conv_text = ""
        for msg in conversation_messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role in ("assistant", "system") and len(content) > 100:
                conv_text += content + "\n\n"

        if not conv_text or len(conv_text) < 200:
            return stats

        # Check if conversation has medical content
        conv_lower = conv_text.lower()
        keyword_matches = sum(1 for kw in medical_keywords if kw in conv_lower)
        if keyword_matches < 2:
            return stats

        # Extract the AI's medical explanations as knowledge
        try:
            chunks = kb.add_document(
                content=conv_text,
                metadata={
                    "source": "Conversation Learning",
                    "type": "conversation_extract",
                    "category": "clinical",
                    "extracted_at": datetime.utcnow().isoformat(),
                    "keyword_density": keyword_matches,
                    "document_id": f"conv_learn_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                },
                chunk_size=1000,
                chunk_overlap=50,
            )
            stats["extracted"] = 1
            stats["indexed"] = chunks
            logger.info(f"[KB_INGEST] Learned from conversation: {chunks} chunks")
        except Exception as e:
            logger.error(f"[KB_INGEST] Conversation learning error: {e}")

        self.state["total_documents_ingested"] += stats["indexed"]
        self._save_state()
        return stats

    def should_fetch_online(self, interval_hours: int = 24) -> bool:
        """Check if enough time has passed for next online fetch"""
        last = self.state.get("last_online_fetch")
        if not last:
            return True
        try:
            last_dt = datetime.fromisoformat(last)
            return datetime.utcnow() - last_dt > timedelta(hours=interval_hours)
        except Exception:
            return True

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "total_documents_ingested": self.state.get("total_documents_ingested", 0),
            "total_online_fetches": self.state.get("total_online_fetches", 0),
            "topics_covered": len(self.state.get("topics_covered", [])),
            "last_online_fetch": self.state.get("last_online_fetch"),
            "last_gap_acquisition": self.state.get("last_gap_acquisition"),
            "recent_fetches": self.state.get("fetch_history", [])[-5:],
        }


# ── Default topics for periodic online fetches ──

CORE_MEDICAL_TOPICS = [
    "diabetes management guidelines 2024",
    "hypertension treatment updates",
    "heart failure management GDMT",
    "COPD exacerbation management",
    "asthma controller therapy",
    "chronic kidney disease staging treatment",
    "stroke acute management tPA",
    "sepsis hour-1 bundle",
    "pneumonia antibiotic guidelines",
    "depression SSRI treatment",
    "anxiety disorder CBT pharmacotherapy",
    "COVID-19 treatment guidelines",
    "antibiotic resistance patterns",
    "opioid prescribing guidelines",
    "cancer screening recommendations",
    "vaccination schedule adults",
    "prenatal care guidelines",
    "pediatric fever management",
    "wound care management",
    "pain management multimodal",
]


# Singleton
_ingester: Optional[KBAutoIngester] = None


def get_kb_ingester() -> KBAutoIngester:
    global _ingester
    if _ingester is None:
        _ingester = KBAutoIngester()
    return _ingester
