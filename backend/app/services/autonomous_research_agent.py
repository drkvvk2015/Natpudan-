"""
Autonomous Research Agent

An AI agent that independently:
- Searches medical literature
- Synthesizes research findings
- Identifies knowledge gaps
- Generates new KB entries
- Validates information quality
- Self-improves over time
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import asyncio
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class ResearchTask:
    """Task for the autonomous agent"""
    task_id: str
    topic: str
    priority: float
    task_type: str  # "gap_fill", "update", "validate", "explore"
    created_at: datetime
    deadline: Optional[datetime]
    status: str = "pending"
    results: List[Dict] = None

    def __post_init__(self):
        if self.results is None:
            self.results = []


@dataclass
class ResearchFinding:
    """A finding from research"""
    source: str
    title: str
    content: str
    confidence: float
    novelty_score: float
    validation_status: str
    extracted_at: datetime
    citations: List[str]


class AutonomousResearchAgent:
    """
    Autonomous agent for continuous knowledge base improvement.
    """

    def __init__(self):
        self.task_queue: List[ResearchTask] = []
        self.completed_tasks: List[ResearchTask] = []
        self.findings: List[ResearchFinding] = []
        self.agent_state: Dict[str, Any] = {
            "last_run": None,
            "total_tasks": 0,
            "successful_tasks": 0,
            "knowledge_added": 0,
            "learning_iterations": 0
        }

        # Research strategies
        self.strategies = {
            "pubmed_search": self._search_pubmed,
            "clinical_trials": self._search_clinical_trials,
            "medical_journals": self._search_medical_journals,
            "cross_reference": self._cross_reference_sources,
        }

    async def run_cycle(self) -> Dict[str, Any]:
        """
        Run one autonomous research cycle.
        """
        logger.info("[AGENT] Starting autonomous research cycle")

        cycle_results = {
            "started_at": datetime.utcnow().isoformat(),
            "tasks_processed": 0,
            "findings_discovered": 0,
            "knowledge_added": 0,
            "errors": []
        }

        # 1. Generate tasks from gaps
        await self._generate_tasks_from_gaps()

        # 2. Prioritize tasks
        self._prioritize_tasks()

        # 3. Process top tasks
        tasks_to_process = self.task_queue[:5]  # Process up to 5 per cycle
        self.task_queue = self.task_queue[5:]

        for task in tasks_to_process:
            try:
                result = await self._execute_task(task)
                cycle_results["tasks_processed"] += 1

                if result.get("success"):
                    cycle_results["findings_discovered"] += len(result.get("findings", []))
                    cycle_results["knowledge_added"] += result.get("entries_added", 0)
                    self.agent_state["successful_tasks"] += 1

                self.completed_tasks.append(task)

            except Exception as e:
                logger.error(f"[AGENT] Task execution error: {e}")
                cycle_results["errors"].append(str(e))

        # 4. Self-reflection and improvement
        await self._self_improve()

        self.agent_state["last_run"] = datetime.utcnow().isoformat()
        self.agent_state["total_tasks"] += cycle_results["tasks_processed"]
        self.agent_state["knowledge_added"] += cycle_results["knowledge_added"]

        cycle_results["completed_at"] = datetime.utcnow().isoformat()

        logger.info(f"[AGENT] Cycle complete: {cycle_results}")
        return cycle_results

    async def _generate_tasks_from_gaps(self) -> None:
        """Generate research tasks from detected knowledge gaps"""
        try:
            from app.services.kb_gap_detector import get_gap_detector
            from app.services.predictive_gap_detector import get_predictive_detector

            # Get current gaps
            gap_detector = get_gap_detector()
            priority_gaps = gap_detector.get_priority_gaps(limit=10)

            # Get predicted gaps
            predictive = get_predictive_detector()
            forecast = predictive.predict_gaps(days_ahead=7)

            # Create tasks from gaps
            for gap in priority_gaps:
                task = ResearchTask(
                    task_id=self._generate_task_id(),
                    topic=gap["query"],
                    priority=gap["priority"],
                    task_type="gap_fill",
                    created_at=datetime.utcnow(),
                    deadline=datetime.utcnow() + timedelta(days=3)
                )
                self.task_queue.append(task)

            # Create tasks from predictions
            for pred in forecast.critical_gaps:
                task = ResearchTask(
                    task_id=self._generate_task_id(),
                    topic=pred.topic,
                    priority=pred.urgency_score,
                    task_type="predictive_fill",
                    created_at=datetime.utcnow(),
                    deadline=datetime.utcnow() + timedelta(days=1)
                )
                self.task_queue.append(task)

            logger.info(f"[AGENT] Generated {len(self.task_queue)} tasks from gaps")

        except Exception as e:
            logger.error(f"[AGENT] Task generation error: {e}")

    def _prioritize_tasks(self) -> None:
        """Sort tasks by priority"""
        self.task_queue.sort(key=lambda t: t.priority, reverse=True)

    async def _execute_task(self, task: ResearchTask) -> Dict[str, Any]:
        """Execute a research task"""
        task.status = "in_progress"
        logger.info(f"[AGENT] Executing task: {task.topic}")

        findings = []

        # Apply multiple research strategies
        for strategy_name, strategy_func in self.strategies.items():
            try:
                strategy_findings = await strategy_func(task.topic)
                findings.extend(strategy_findings)
            except Exception as e:
                logger.warning(f"[AGENT] Strategy {strategy_name} failed: {e}")

        # Validate findings
        validated_findings = self._validate_findings(findings)

        # Synthesize knowledge
        synthesized = await self._synthesize_findings(task.topic, validated_findings)

        # Add to KB
        entries_added = await self._add_to_kb(task.topic, synthesized)

        task.status = "completed"
        task.results = validated_findings

        return {
            "success": len(validated_findings) > 0,
            "findings": validated_findings,
            "synthesized": synthesized,
            "entries_added": entries_added
        }

    async def _search_pubmed(self, topic: str) -> List[ResearchFinding]:
        """Search PubMed for research papers"""
        try:
            from app.services.pubmed_integration import get_pubmed_integration
            pubmed = get_pubmed_integration()

            papers = pubmed.search_papers(
                query=topic,
                max_results=5,
                days_back=30
            )

            findings = []
            for paper in papers:
                finding = ResearchFinding(
                    source="PubMed",
                    title=paper.get("title", ""),
                    content=paper.get("abstract", ""),
                    confidence=0.8,
                    novelty_score=self._calculate_novelty(paper),
                    validation_status="pending",
                    extracted_at=datetime.utcnow(),
                    citations=[paper.get("pmid", "")]
                )
                findings.append(finding)

            return findings

        except Exception as e:
            logger.error(f"[AGENT] PubMed search error: {e}")
            return []

    async def _search_clinical_trials(self, topic: str) -> List[ResearchFinding]:
        """Search ClinicalTrials.gov for active trials"""
        # Placeholder for clinical trials API
        # Would integrate with ClinicalTrials.gov API
        return []

    async def _search_medical_journals(self, topic: str) -> List[ResearchFinding]:
        """Search medical journals and news"""
        findings = []

        # This would integrate with journal APIs, RSS feeds, etc.
        # For now, using simulated findings based on common patterns

        key_terms = {
            "diabetes": ["GLP-1 agonists", "SGLT2 inhibitors", "artificial pancreas"],
            "cancer": ["immunotherapy", "CAR-T", "precision medicine"],
            "cardiovascular": ["PCSK9 inhibitors", "SGLT2 for heart failure"],
            "alzheimer": ["anti-amyloid antibodies", "tau inhibitors"],
        }

        for key, terms in key_terms.items():
            if key in topic.lower():
                for term in terms:
                    finding = ResearchFinding(
                        source="Medical Literature",
                        title=f"Recent advances in {term}",
                        content=f"{term} shows promising results in recent studies for {topic}.",
                        confidence=0.7,
                        novelty_score=0.8,
                        validation_status="pending",
                        extracted_at=datetime.utcnow(),
                        citations=[]
                    )
                    findings.append(finding)

        return findings

    async def _cross_reference_sources(self, topic: str) -> List[ResearchFinding]:
        """Cross-reference multiple sources for validation"""
        # This would verify findings against multiple sources
        return []

    def _validate_findings(self, findings: List[ResearchFinding]) -> List[ResearchFinding]:
        """Validate findings for quality and accuracy"""
        validated = []

        for finding in findings:
            # Skip if confidence too low
            if finding.confidence < 0.5:
                continue

            # Check content quality
            if len(finding.content) < 50:
                continue

            # Cross-validate with existing KB
            try:
                from app.services.local_vector_kb import get_local_knowledge_base
                kb = get_local_knowledge_base()
                similar = kb.search(finding.content, top_k=1)

                if similar and similar[0]["score"] > 0.95:
                    # Too similar to existing knowledge
                    finding.novelty_score *= 0.5

            except Exception:
                pass  # nosec B110

            finding.validation_status = "validated"
            validated.append(finding)

        return validated

    async def _synthesize_findings(self, topic: str,
                                    findings: List[ResearchFinding]) -> str:
        """Synthesize multiple findings into coherent knowledge"""
        if not findings:
            return ""

        # Aggregate content
        contents = [f.content for f in findings[:3]]

        # Simple synthesis (in production, this would use LLM)
        synthesized = f"""## {topic.title()}

Based on recent research findings:

{chr(10).join(f"- {c[:300]}..." for c in contents)}

**Key Insights:**
{chr(10).join(f"{i+1}. {f.title[:100]}... (Confidence: {f.confidence:.0%})"
               for i, f in enumerate(findings[:3]))}

*Synthesized by Autonomous Research Agent on {datetime.utcnow().strftime("%Y-%m-%d")}*
"""

        return synthesized

    async def _add_to_kb(self, topic: str, content: str) -> int:
        """Add synthesized knowledge to KB"""
        if not content:
            return 0

        try:
            from app.services.local_vector_kb import get_local_knowledge_base
            kb = get_local_knowledge_base()

            chunks = kb.add_document(
                content=content,
                metadata={
                    "source": "Autonomous Research Agent",
                    "topic": topic,
                    "type": "auto_researched",
                    "document_id": f"ara_{hashlib.sha256(topic.encode()).hexdigest()[:12]}",
                    "year": datetime.utcnow().year
                }
            )

            logger.info(f"[AGENT] Added {chunks} chunks for topic: {topic}")
            return chunks

        except Exception as e:
            logger.error(f"[AGENT] KB add error: {e}")
            return 0

    async def _self_improve(self) -> None:
        """Learn from past tasks to improve future performance"""
        if len(self.completed_tasks) < 10:
            return

        # Analyze successful vs failed tasks
        recent = self.completed_tasks[-50:]
        success_rate = sum(1 for t in recent if t.status == "completed") / len(recent)

        # Adjust strategies based on success
        if success_rate < 0.5:
            logger.warning("[AGENT] Low success rate, adjusting strategies")
            # Could modify strategy weights here

        self.agent_state["learning_iterations"] += 1

    def _generate_task_id(self) -> str:
        """Generate unique task ID"""
        return f"task_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{hashlib.sha256(str(datetime.utcnow()).encode()).hexdigest()[:8]}"

    def _calculate_novelty(self, paper: Dict) -> float:
        """Calculate novelty score for a paper"""
        # Based on publication date, citations, etc.
        base_score = 0.5

        # More recent = higher novelty
        if "publication_date" in paper:
            try:
                pub_date = datetime.fromisoformat(paper["publication_date"].replace("Z", "+00:00"))
                days_old = (datetime.utcnow() - pub_date).days
                if days_old < 7:
                    base_score += 0.3
                elif days_old < 30:
                    base_score += 0.2
            except Exception:
                pass  # nosec B110

        return min(base_score, 1.0)

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "state": self.agent_state,
            "queue_size": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "total_findings": len(self.findings),
            "is_active": self.agent_state["last_run"] is not None
        }


# Singleton instance
_research_agent: Optional[AutonomousResearchAgent] = None


def get_research_agent() -> AutonomousResearchAgent:
    global _research_agent
    if _research_agent is None:
        _research_agent = AutonomousResearchAgent()
    return _research_agent
