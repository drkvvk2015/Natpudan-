"""
Automated Knowledge Base Manager
- Scheduled PubMed syncing
- Freshness tagging & decay policies
- Quality gates before indexing
- Index integrity monitoring
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from pathlib import Path
import json
import hashlib

logger = logging.getLogger(__name__)


class AutomatedKBManager:
    """
    Manages automated KB growth, freshness, and quality.
    """
    
    def __init__(self):
        self.feedback_dir = Path("data/kb_feedback")
        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        self.quality_config = {
            "min_text_length": 100,  # Minimum chars to accept
            "min_entities": 3,  # Min medical entities (diseases, drugs, etc.)
            "require_metadata": ["filename", "document_id", "category"],  # Required fields
            "quality_score_threshold": 0.5  # 0-1, higher = stricter
        }
    
    # ================== FRESHNESS POLICY ==================
    def calculate_freshness_score(self, doc_metadata: Dict[str, Any]) -> float:
        """
        Calculate freshness score for a document (0-1).
        Recent = high score. Old clinical content = lower score.
        """
        if "year" not in doc_metadata:
            return 0.5  # Unknown age = neutral
        
        try:
            year = int(doc_metadata["year"])
            current_year = datetime.now().year
            age_years = current_year - year
            
            # Decay function: 0 years old = 1.0, 5+ years = 0.5, 10+ years = 0.2
            if age_years <= 0:
                score = 1.0
            elif age_years <= 2:
                score = 0.95 - (age_years * 0.02)
            elif age_years <= 5:
                score = 0.91 - ((age_years - 2) * 0.08)
            else:
                score = max(0.2, 0.75 - (age_years * 0.05))
            
            return max(0.0, min(1.0, score))
        except:
            return 0.5
    
    def apply_freshness_tags(self, doc_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add freshness tags to document metadata.
        """
        score = self.calculate_freshness_score(doc_metadata)
        doc_metadata["freshness_score"] = score
        
        # Mark as outdated if very old and clinical
        if score < 0.4 and doc_metadata.get("category") == "clinical_guideline":
            doc_metadata["outdated"] = True
            doc_metadata["freshness_status"] = "outdated"
        elif score >= 0.8:
            doc_metadata["freshness_status"] = "current"
        elif score >= 0.5:
            doc_metadata["freshness_status"] = "aging"
        else:
            doc_metadata["freshness_status"] = "historical"
        
        doc_metadata["freshness_evaluated_at"] = datetime.now().isoformat()
        return doc_metadata
    
    # ================== QUALITY GATE ==================
    def check_quality_gate(self, text: str, metadata: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate document quality before indexing.
        Returns (passes, reason_if_fails)
        """
        # Check text length
        if len(text.strip()) < self.quality_config["min_text_length"]:
            return False, f"Text too short ({len(text)} < {self.quality_config['min_text_length']})"
        
        # Check required metadata
        missing = [k for k in self.quality_config["require_metadata"] if k not in metadata or not metadata[k]]
        if missing:
            return False, f"Missing required metadata: {', '.join(missing)}"
        
        # Check for medical entities (simple heuristic)
        medical_terms = {
            "disease", "symptom", "treatment", "diagnosis", "medication", "drug",
            "therapy", "condition", "patient", "clinical", "medical", "hospital",
            "syndrome", "inflammation", "infection", "cancer", "diabetes", "pressure",
            "hypertension", "asthma", "pneumonia", "injury", "pain", "fever", "procedure"
        }
        text_lower = text.lower()
        entity_count = sum(1 for term in medical_terms if term in text_lower)
        
        if entity_count < self.quality_config["min_entities"]:
            return False, f"Insufficient medical content ({entity_count} terms found)"
        
        return True, "Passed quality gate"
    
    # ================== FEEDBACK TRACKING ==================
    def record_answer_feedback(
        self,
        answer_id: str,
        query: str,
        document_ids: List[str],
        rating: int,  # 1-5
        user_comment: str = ""
    ) -> Dict[str, Any]:
        """
        Record user feedback on an answer for learning.
        """
        feedback = {
            "answer_id": answer_id,
            "query": query,
            "document_ids": document_ids,
            "rating": rating,
            "comment": user_comment,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save to file (in production, use database)
        feedback_file = self.feedback_dir / f"{answer_id}.json"
        with open(feedback_file, 'w') as f:
            json.dump(feedback, f)
        
        # Update document weights based on feedback
        if rating >= 4:
            # Boost: increase re-ranking weight
            for doc_id in document_ids:
                self._update_doc_weight(doc_id, boost=0.1)
        elif rating <= 2:
            # Demote: decrease weight or trigger re-chunking
            for doc_id in document_ids:
                self._update_doc_weight(doc_id, boost=-0.2)
        
        logger.info(f"Feedback recorded: answer={answer_id}, rating={rating}")
        return feedback
    
    def _update_doc_weight(self, doc_id: str, boost: float):
        """Update document weight based on feedback"""
        weight_file = self.feedback_dir / f"{doc_id}_weight.json"
        
        if weight_file.exists():
            with open(weight_file, 'r') as f:
                data = json.load(f)
        else:
            data = {"doc_id": doc_id, "weight": 1.0, "feedback_count": 0}
        
        data["weight"] = max(0.1, min(2.0, data["weight"] + boost))
        data["feedback_count"] += 1
        data["last_feedback"] = datetime.now().isoformat()
        
        with open(weight_file, 'w') as f:
            json.dump(data, f)
    
    def get_doc_weight(self, doc_id: str) -> float:
        """Get current weight multiplier for a document"""
        weight_file = self.feedback_dir / f"{doc_id}_weight.json"
        if weight_file.exists():
            with open(weight_file, 'r') as f:
                return json.load(f).get("weight", 1.0)
        return 1.0
    
    # ================== INDEX INTEGRITY ==================
    async def check_index_integrity(self) -> Dict[str, Any]:
        """
        Check FAISS index consistency and metadata alignment.
        """
        try:
            from app.services.local_vector_kb import get_local_knowledge_base
            local_kb = get_local_knowledge_base()
            
            stats = local_kb.get_statistics()
            
            # Check for metadata mismatches
            issues = []
            
            if not hasattr(local_kb, 'documents'):
                return {"status": "error", "message": "Cannot access KB documents"}
            
            # Verify all docs have required fields
            for doc in local_kb.documents:
                if not doc.get("document_id"):
                    issues.append(f"Doc missing document_id: {doc.get('filename', 'unknown')}")
                if not doc.get("filename"):
                    issues.append(f"Doc missing filename: {doc.get('document_id', 'unknown')}")
            
            # Check index size matches document count
            if hasattr(local_kb, 'index') and local_kb.index:
                index_size = local_kb.index.ntotal if hasattr(local_kb.index, 'ntotal') else 0
                doc_count = len(local_kb.documents)
                
                if abs(index_size - doc_count) > 10:  # Allow small drift
                    issues.append(f"Index drift: {index_size} vectors vs {doc_count} docs")
            
            return {
                "status": "ok" if not issues else "warning",
                "timestamp": datetime.now().isoformat(),
                "index_stats": stats,
                "issues": issues,
                "integrity_check_passed": len(issues) == 0
            }
        
        except Exception as e:
            logger.error(f"Index integrity check failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def rebuild_index_if_needed(self) -> Dict[str, Any]:
        """
        Rebuild KB index if integrity issues detected.
        """
        integrity = await self.check_index_integrity()
        
        if integrity.get("status") == "ok":
            return {"action": "no_rebuild_needed", **integrity}
        
        try:
            logger.warning("Rebuilding KB index due to integrity issues...")
            
            from app.services.local_vector_kb import get_local_knowledge_base
            local_kb = get_local_knowledge_base()
            
            # Re-initialize index
            if hasattr(local_kb, '_initialize_new_index'):
                local_kb._initialize_new_index()
            
            if hasattr(local_kb, '_save_index'):
                local_kb._save_index()
            
            logger.info("KB index rebuilt successfully")
            return {
                "action": "rebuild_completed",
                "timestamp": datetime.now().isoformat(),
                "issues_fixed": integrity.get("issues", [])
            }
        
        except Exception as e:
            logger.error(f"Failed to rebuild index: {e}")
            return {
                "action": "rebuild_failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # ================== AUTOMATED PUBMED SYNC ==================
    async def sync_pubmed_to_kb(
        self,
        queries: List[str],
        max_results_per_query: int = 10
    ) -> Dict[str, Any]:
        """
        Automatically fetch new PubMed articles and add to local KB.
        Runs nightly to keep medical literature fresh.
        """
        from app.services.online_knowledge_service import OnlineKnowledgeService
        from app.services.local_vector_kb import get_local_knowledge_base
        
        online_service = OnlineKnowledgeService()
        local_kb = get_local_knowledge_base()
        
        total_added = 0
        total_failed = 0
        added_by_query = {}
        
        for query in queries:
            logger.info(f"[PUBMED-SYNC] Fetching: {query}")
            
            try:
                articles = await online_service.search_pubmed(query, max_results=max_results_per_query)
                query_added = 0
                
                for article in articles:
                    try:
                        # Prepare article text for KB
                        article_text = f"""
Title: {article.get('title', 'Unknown')}
Authors: {article.get('authors', 'Unknown')}
Year: {article.get('year', 'Unknown')}
Abstract: {article.get('abstract', 'No abstract')}
URL: {article.get('url', 'N/A')}
"""
                        
                        # Create metadata
                        metadata = {
                            "filename": f"pubmed_{article.get('pmid', 'unknown')}.pdf",
                            "document_id": f"pubmed_{article.get('pmid', 'unknown')}",
                            "category": "pubmed_auto",
                            "section": "research",
                            "year": int(article.get('year', datetime.now().year)),
                            "source": "PubMed",
                            "pmid": article.get('pmid'),
                            "sync_timestamp": datetime.now().isoformat(),
                            "query": query
                        }
                        
                        # Apply quality gate
                        passes, reason = self.check_quality_gate(article_text, metadata)
                        if not passes:
                            logger.debug(f"Article rejected: {reason}")
                            continue
                        
                        # Apply freshness tags
                        metadata = self.apply_freshness_tags(metadata)
                        
                        # Add to KB
                        chunks_added = local_kb.add_document(
                            content=article_text,
                            metadata=metadata,
                            chunk_size=1500,
                            chunk_overlap=100
                        )
                        
                        if chunks_added > 0:
                            query_added += 1
                            total_added += chunks_added
                            logger.info(f"[OK] Added PubMed article: {article.get('title', 'Unknown')} ({chunks_added} chunks)")
                    
                    except Exception as e:
                        logger.warning(f"Failed to add article: {e}")
                        total_failed += 1
                
                added_by_query[query] = query_added
            
            except Exception as e:
                logger.error(f"Error syncing query '{query}': {e}")
                added_by_query[query] = 0
        
        result = {
            "action": "pubmed_sync",
            "timestamp": datetime.now().isoformat(),
            "total_articles_added": total_added,
            "total_failed": total_failed,
            "by_query": added_by_query,
            "queries_synced": len(queries)
        }
        
        logger.info(f"[PUBMED-SYNC] Complete: {total_added} chunks added from {len(queries)} queries")
        return result
    
    # ================== REFRESH OPERATIONS ==================
    async def run_daily_refresh(self) -> Dict[str, Any]:
        """
        Daily maintenance job:
        - Sync new PubMed articles
        - Check index integrity
        - Apply freshness tags to old docs
        - Clean expired cache
        """
        logger.info("[KB-REFRESH] Starting daily refresh cycle...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "operations": {}
        }
        
        # Sync PubMed
        pubmed_queries = [
            "recent clinical guidelines 2024",
            "emerging disease diagnosis",
            "pharmacotherapy updates",
            "patient management protocols",
            "diagnostic imaging techniques"
        ]
        
        try:
            pubmed_result = await self.sync_pubmed_to_kb(pubmed_queries, max_results_per_query=5)
            results["operations"]["pubmed_sync"] = pubmed_result
        except Exception as e:
            logger.error(f"PubMed sync failed: {e}")
            results["operations"]["pubmed_sync"] = {"error": str(e)}
        
        # Check index integrity
        try:
            integrity_result = await self.check_index_integrity()
            results["operations"]["index_integrity"] = integrity_result
            
            # Rebuild if needed
            if not integrity_result.get("integrity_check_passed"):
                rebuild_result = await self.rebuild_index_if_needed()
                results["operations"]["index_rebuild"] = rebuild_result
        except Exception as e:
            logger.error(f"Index check failed: {e}")
            results["operations"]["index_integrity"] = {"error": str(e)}
        
        # Apply freshness tags to existing docs
        try:
            from app.services.local_vector_kb import get_local_knowledge_base
            local_kb = get_local_knowledge_base()
            
            refreshed_count = 0
            if hasattr(local_kb, 'documents'):
                for doc in local_kb.documents:
                    self.apply_freshness_tags(doc)
                    refreshed_count += 1
            
            if hasattr(local_kb, '_save_index'):
                local_kb._save_index()
            
            results["operations"]["freshness_refresh"] = {
                "docs_refreshed": refreshed_count,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Freshness refresh failed: {e}")
            results["operations"]["freshness_refresh"] = {"error": str(e)}
        
        logger.info("[KB-REFRESH] Daily refresh cycle complete")
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get KB automation statistics"""
        import os
        feedback_files = list(self.feedback_dir.glob("*.json"))
        
        return {
            "feedback_records": len([f for f in feedback_files if "_weight" not in f.name]),
            "documents_with_feedback": len([f for f in feedback_files if "_weight" in f.name]),
            "quality_config": self.quality_config,
            "feedback_dir": str(self.feedback_dir)
        }


# Singleton
_automated_kb_manager = None

def get_automated_kb_manager() -> AutomatedKBManager:
    global _automated_kb_manager
    if _automated_kb_manager is None:
        _automated_kb_manager = AutomatedKBManager()
    return _automated_kb_manager
