"""
Knowledge Gap Detector
Tracks queries with poor/no KB results, identifies knowledge gaps,
and queues topics for automatic knowledge acquisition.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class KnowledgeGapDetector:
    """
    Monitors search quality and detects knowledge gaps.

    Tracks:
    - Queries that return no results
    - Queries with low-confidence results (score < threshold)
    - Frequently asked topics not well-covered in KB
    - User feedback signals (if available)

    Outputs:
    - Gap report with prioritized topics for acquisition
    - Queue of topics to fetch from online sources
    """

    def __init__(self, storage_dir: str = "data/knowledge_base"):
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.storage_path = os.path.join(backend_dir, storage_dir, "knowledge_gaps.json")
        self.min_score_threshold = 0.3  # Below this = gap
        self.max_gap_entries = 5000
        self.gaps: Dict[str, Any] = self._load_gaps()

    def _load_gaps(self) -> Dict[str, Any]:
        """Load gap data from disk"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass  # nosec B110
        return {
            "queries": {},          # query_normalized -> {count, last_seen, best_score, resolved}
            "acquisition_queue": [], # [{topic, priority, source, queued_at}]
            "stats": {"total_queries": 0, "gaps_detected": 0, "gaps_resolved": 0},
        }

    def _save_gaps(self):
        """Persist gap data to disk"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        try:
            with open(self.storage_path, "w") as f:
                json.dump(self.gaps, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"[GAP_DETECT] Failed to save: {e}")

    def _normalize_query(self, query: str) -> str:
        """Normalize query for deduplication"""
        return " ".join(query.lower().strip().split())

    def record_search(self, query: str, results: List[Dict], top_score: float = 0.0):
        """
        Record a search and detect if it's a knowledge gap.

        Args:
            query: User's search query
            results: Search results returned
            top_score: Best similarity score from results
        """
        normalized = self._normalize_query(query)
        if not normalized or len(normalized) < 3:
            return

        self.gaps["stats"]["total_queries"] = self.gaps["stats"].get("total_queries", 0) + 1

        is_gap = len(results) == 0 or top_score < self.min_score_threshold

        if normalized not in self.gaps["queries"]:
            self.gaps["queries"][normalized] = {
                "count": 0,
                "first_seen": datetime.utcnow().isoformat(),
                "last_seen": None,
                "best_score": 0.0,
                "is_gap": False,
                "resolved": False,
            }

        entry = self.gaps["queries"][normalized]
        entry["count"] += 1
        entry["last_seen"] = datetime.utcnow().isoformat()
        entry["best_score"] = max(entry.get("best_score", 0), top_score)

        if is_gap and not entry.get("resolved", False):
            entry["is_gap"] = True
            self.gaps["stats"]["gaps_detected"] = self.gaps["stats"].get("gaps_detected", 0) + 1
            logger.debug(f"[GAP_DETECT] Gap found: '{normalized}' (score={top_score:.2f})")

        # Trim old entries if over limit
        if len(self.gaps["queries"]) > self.max_gap_entries:
            self._trim_old_entries()

        self._save_gaps()

    def mark_resolved(self, query: str):
        """Mark a gap as resolved after knowledge acquisition"""
        normalized = self._normalize_query(query)
        if normalized in self.gaps["queries"]:
            self.gaps["queries"][normalized]["resolved"] = True
            self.gaps["queries"][normalized]["is_gap"] = False
            self.gaps["stats"]["gaps_resolved"] = self.gaps["stats"].get("gaps_resolved", 0) + 1
            self._save_gaps()

    def get_priority_gaps(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get top knowledge gaps sorted by priority.
        Priority = frequency * recency_weight * (1 - best_score)

        Returns:
            List of gap entries with priority scores
        """
        gaps = []
        now = datetime.utcnow()

        for query, data in self.gaps.get("queries", {}).items():
            if not data.get("is_gap") or data.get("resolved"):
                continue

            count = data.get("count", 1)
            best_score = data.get("best_score", 0)

            # Recency weight: more recent = higher priority
            last_seen = data.get("last_seen")
            if last_seen:
                try:
                    last_dt = datetime.fromisoformat(last_seen)
                    days_ago = (now - last_dt).days
                    recency = max(0.1, 1.0 - (days_ago / 30))  # Decay over 30 days
                except Exception:
                    recency = 0.5
            else:
                recency = 0.5

            priority = count * recency * (1.0 - best_score)

            gaps.append({
                "query": query,
                "count": count,
                "best_score": best_score,
                "last_seen": last_seen,
                "priority": round(priority, 3),
            })

        gaps.sort(key=lambda x: x["priority"], reverse=True)
        return gaps[:limit]

    def get_acquisition_topics(self, limit: int = 10) -> List[str]:
        """Get topic list for online knowledge acquisition"""
        priority_gaps = self.get_priority_gaps(limit=limit)
        return [g["query"] for g in priority_gaps]

    def get_statistics(self) -> Dict[str, Any]:
        """Get gap detection statistics"""
        total_queries = len(self.gaps.get("queries", {}))
        active_gaps = sum(
            1 for q in self.gaps.get("queries", {}).values()
            if q.get("is_gap") and not q.get("resolved")
        )
        resolved = sum(
            1 for q in self.gaps.get("queries", {}).values()
            if q.get("resolved")
        )

        return {
            "total_tracked_queries": total_queries,
            "active_gaps": active_gaps,
            "resolved_gaps": resolved,
            "total_searches_recorded": self.gaps.get("stats", {}).get("total_queries", 0),
            "top_gaps": self.get_priority_gaps(limit=5),
        }

    def _trim_old_entries(self):
        """Remove oldest resolved entries to keep storage manageable"""
        resolved = [
            (k, v) for k, v in self.gaps["queries"].items()
            if v.get("resolved")
        ]
        resolved.sort(key=lambda x: x[1].get("last_seen", ""), reverse=False)

        # Remove oldest resolved entries
        to_remove = len(self.gaps["queries"]) - self.max_gap_entries + 500
        for key, _ in resolved[:to_remove]:
            del self.gaps["queries"][key]


# Singleton
_gap_detector: Optional[KnowledgeGapDetector] = None


def get_gap_detector() -> KnowledgeGapDetector:
    global _gap_detector
    if _gap_detector is None:
        _gap_detector = KnowledgeGapDetector()
    return _gap_detector
