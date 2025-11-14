"""
PubMed Integration Service
Automatically fetches latest medical research papers from PubMed
"""

import logging
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)


class PubMedIntegration:
    """
    Integrates with PubMed API to fetch latest medical research.
    Auto-updates knowledge base with new papers.
    """
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(self, email: Optional[str] = None):
        """
        Initialize PubMed integration.
        
        Args:
            email: Email for PubMed API (recommended for higher rate limits)
        """
        self.email = email
        self.session = requests.Session()
        logger.info("PubMed integration initialized")
    
    def search_papers(
        self,
        query: str,
        max_results: int = 10,
        days_back: int = 30,
        sort: str = "relevance"
    ) -> List[Dict[str, Any]]:
        """
        Search PubMed for papers.
        
        Args:
            query: Search query (e.g., "diabetes treatment")
            max_results: Maximum papers to return
            days_back: Only include papers from last N days (0 = all time)
            sort: Sort order ("relevance" or "date")
            
        Returns:
            List of paper metadata
        """
        try:
            # Build date filter
            date_filter = ""
            if days_back > 0:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days_back)
                date_filter = f" AND {start_date.strftime('%Y/%m/%d')}:{end_date.strftime('%Y/%m/%d')}[PDAT]"
            
            # Search PubMed
            search_params = {
                "db": "pubmed",
                "term": query + date_filter,
                "retmax": max_results,
                "sort": sort,
                "retmode": "json"
            }
            
            if self.email:
                search_params["email"] = self.email
            
            search_response = self.session.get(
                f"{self.BASE_URL}/esearch.fcgi",
                params=search_params,
                timeout=10
            )
            search_response.raise_for_status()
            search_data = search_response.json()
            
            # Get paper IDs
            id_list = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not id_list:
                logger.info(f"No papers found for query: {query}")
                return []
            
            # Fetch paper details
            papers = self._fetch_paper_details(id_list)
            
            logger.info(f"Found {len(papers)} papers for query: {query}")
            return papers
            
        except Exception as e:
            logger.error(f"Error searching PubMed: {e}")
            return []
    
    def _fetch_paper_details(self, pubmed_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch detailed information for PubMed IDs.
        
        Args:
            pubmed_ids: List of PubMed IDs
            
        Returns:
            List of paper details
        """
        try:
            # Fetch summaries
            summary_params = {
                "db": "pubmed",
                "id": ",".join(pubmed_ids),
                "retmode": "xml"
            }
            
            if self.email:
                summary_params["email"] = self.email
            
            summary_response = self.session.get(
                f"{self.BASE_URL}/esummary.fcgi",
                params=summary_params,
                timeout=15
            )
            summary_response.raise_for_status()
            
            # Parse XML response
            import xml.etree.ElementTree as ET
            root = ET.fromstring(summary_response.content)
            
            papers = []
            for doc_sum in root.findall(".//DocSum"):
                paper = self._parse_document_summary(doc_sum)
                if paper:
                    papers.append(paper)
            
            # Rate limiting
            time.sleep(0.34)  # Max 3 requests/second without API key
            
            return papers
            
        except Exception as e:
            logger.error(f"Error fetching paper details: {e}")
            return []
    
    def _parse_document_summary(self, doc_sum) -> Optional[Dict[str, Any]]:
        """Parse PubMed document summary XML"""
        try:
            pubmed_id = doc_sum.find("./Id").text
            
            # Extract fields
            title = self._get_item_value(doc_sum, "Title")
            authors = self._get_item_value(doc_sum, "AuthorList")
            pub_date = self._get_item_value(doc_sum, "PubDate")
            source = self._get_item_value(doc_sum, "Source")
            abstract = self._get_item_value(doc_sum, "Abstract")
            
            return {
                "pubmed_id": pubmed_id,
                "title": title or "Untitled",
                "authors": authors or "Unknown",
                "publication_date": pub_date or "Unknown",
                "journal": source or "Unknown",
                "abstract": abstract or "",
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/",
                "fetched_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing document summary: {e}")
            return None
    
    def _get_item_value(self, doc_sum, item_name: str) -> Optional[str]:
        """Extract item value from document summary"""
        item = doc_sum.find(f".//Item[@Name='{item_name}']")
        if item is not None:
            return item.text
        return None
    
    def fetch_latest_research(
        self,
        topics: List[str],
        papers_per_topic: int = 5,
        days_back: int = 7
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch latest research for multiple topics.
        
        Args:
            topics: List of medical topics
            papers_per_topic: Papers to fetch per topic
            days_back: Days to look back
            
        Returns:
            Dictionary mapping topics to papers
        """
        results = {}
        
        for topic in topics:
            logger.info(f"Fetching latest papers for: {topic}")
            papers = self.search_papers(
                query=topic,
                max_results=papers_per_topic,
                days_back=days_back,
                sort="date"
            )
            results[topic] = papers
            
            # Rate limiting between queries
            time.sleep(0.5)
        
        return results
    
    def format_paper_for_indexing(
        self,
        paper: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format paper for knowledge base indexing.
        
        Args:
            paper: Paper metadata
            
        Returns:
            Formatted document for indexing
        """
        # Create comprehensive text content
        content_parts = [
            f"Title: {paper['title']}",
            f"Authors: {paper['authors']}",
            f"Journal: {paper['journal']}",
            f"Published: {paper['publication_date']}",
            f"\nAbstract:\n{paper['abstract']}",
        ]
        
        return {
            "content": "\n\n".join(content_parts),
            "metadata": {
                "source": "PubMed",
                "document_id": f"pubmed_{paper['pubmed_id']}",
                "title": paper['title'],
                "pubmed_id": paper['pubmed_id'],
                "url": paper['url'],
                "publication_date": paper['publication_date'],
                "journal": paper['journal'],
                "fetched_at": paper['fetched_at']
            }
        }
    
    def auto_update_knowledge_base(
        self,
        vector_kb,
        topics: List[str],
        papers_per_topic: int = 3,
        days_back: int = 7
    ) -> Dict[str, Any]:
        """
        Automatically update knowledge base with latest research.
        
        Args:
            vector_kb: Vector knowledge base instance
            topics: Topics to track
            papers_per_topic: Papers per topic
            days_back: Days to look back
            
        Returns:
            Update summary
        """
        logger.info(f"Auto-updating knowledge base for {len(topics)} topics")
        
        # Fetch latest papers
        all_papers = self.fetch_latest_research(
            topics=topics,
            papers_per_topic=papers_per_topic,
            days_back=days_back
        )
        
        # Index papers
        indexed_count = 0
        errors = []
        
        for topic, papers in all_papers.items():
            for paper in papers:
                try:
                    # Format for indexing
                    doc = self.format_paper_for_indexing(paper)
                    
                    # Add to vector KB
                    vector_kb.add_document(
                        content=doc["content"],
                        metadata=doc["metadata"]
                    )
                    
                    indexed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error indexing paper {paper.get('pubmed_id')}: {e}")
                    errors.append({
                        "pubmed_id": paper.get('pubmed_id'),
                        "error": str(e)
                    })
        
        return {
            "topics_searched": len(topics),
            "papers_found": sum(len(p) for p in all_papers.values()),
            "papers_indexed": indexed_count,
            "errors": errors,
            "timestamp": datetime.utcnow().isoformat()
        }


# Global instance
_pubmed_integration = None

def get_pubmed_integration() -> PubMedIntegration:
    """Get or create PubMed integration instance"""
    global _pubmed_integration
    if _pubmed_integration is None:
        _pubmed_integration = PubMedIntegration()
    return _pubmed_integration
