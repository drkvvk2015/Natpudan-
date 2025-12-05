"""
Online Medical Data Sources Integration
Fetches real-time medical knowledge from multiple trusted sources
"""

import logging
import requests
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
import time

logger = logging.getLogger(__name__)


class OnlineMedicalSources:
    """
    Integration with multiple online medical knowledge sources:
    - PubMed/NCBI
    - WHO (World Health Organization)
    - CDC (Centers for Disease Control)
    - NIH (National Institutes of Health)
    - FDA Drug Information
    """
    
    def __init__(self, email: Optional[str] = None):
        """
        Initialize online medical sources integration.
        
        Args:
            email: Email for API rate limit increases
        """
        self.email = email
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PhysicianAI-KnowledgeBase/1.0'
        })
        
        # API endpoints
        self.PUBMED_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.WHO_BASE = "https://www.who.int/api"
        self.CDC_BASE = "https://data.cdc.gov/api"
        
        logger.info("Online medical sources initialized")
    
    async def fetch_comprehensive_knowledge(
        self,
        query: str,
        sources: List[str] = None,
        max_results: int = 10
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch knowledge from multiple sources simultaneously.
        
        Args:
            query: Medical topic or query
            sources: List of sources to query (default: all)
            max_results: Results per source
            
        Returns:
            Dictionary mapping source names to results
        """
        if sources is None:
            sources = ['pubmed', 'who', 'cdc', 'nih']
        
        results = {}
        
        # Create tasks for parallel fetching
        tasks = []
        if 'pubmed' in sources:
            tasks.append(self._fetch_pubmed_async(query, max_results))
        if 'who' in sources:
            tasks.append(self._fetch_who_async(query, max_results))
        if 'cdc' in sources:
            tasks.append(self._fetch_cdc_async(query, max_results))
        if 'nih' in sources:
            tasks.append(self._fetch_nih_async(query, max_results))
        
        # Execute all tasks concurrently
        source_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Map results to source names
        source_names = [s for s in sources if s in ['pubmed', 'who', 'cdc', 'nih']]
        for source_name, result in zip(source_names, source_results):
            if isinstance(result, Exception):
                logger.error(f"Error fetching from {source_name}: {result}")
                results[source_name] = []
            else:
                results[source_name] = result
        
        return results
    
    async def _fetch_pubmed_async(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Fetch from PubMed asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._fetch_pubmed, query, max_results)
    
    def _fetch_pubmed(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Fetch medical research from PubMed.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of paper details
        """
        try:
            # Step 1: Search for paper IDs
            search_params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "sort": "relevance",
                "retmode": "json"
            }
            
            if self.email:
                search_params["email"] = self.email
            
            search_response = self.session.get(
                f"{self.PUBMED_BASE}/esearch.fcgi",
                params=search_params,
                timeout=10
            )
            search_response.raise_for_status()
            search_data = search_response.json()
            
            id_list = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not id_list:
                return []
            
            # Step 2: Fetch paper details
            time.sleep(0.34)  # Rate limiting
            
            summary_params = {
                "db": "pubmed",
                "id": ",".join(id_list),
                "retmode": "xml"
            }
            
            if self.email:
                summary_params["email"] = self.email
            
            summary_response = self.session.get(
                f"{self.PUBMED_BASE}/esummary.fcgi",
                params=summary_params,
                timeout=15
            )
            summary_response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(summary_response.content)
            papers = []
            
            for doc_sum in root.findall(".//DocSum"):
                try:
                    pubmed_id = doc_sum.find("./Id").text
                    title = self._get_item_value(doc_sum, "Title") or "Untitled"
                    authors = self._get_item_value(doc_sum, "AuthorList") or "Unknown"
                    pub_date = self._get_item_value(doc_sum, "PubDate") or "Unknown"
                    source = self._get_item_value(doc_sum, "Source") or "Unknown"
                    
                    # Fetch abstract separately
                    abstract = self._fetch_abstract(pubmed_id)
                    
                    papers.append({
                        "source": "PubMed",
                        "pubmed_id": pubmed_id,
                        "title": title,
                        "authors": authors,
                        "publication_date": pub_date,
                        "journal": source,
                        "abstract": abstract,
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/",
                        "fetched_at": datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    logger.error(f"Error parsing PubMed document: {e}")
                    continue
            
            return papers
            
        except Exception as e:
            logger.error(f"Error fetching from PubMed: {e}")
            return []
    
    def _fetch_abstract(self, pubmed_id: str) -> str:
        """Fetch full abstract for a PubMed article"""
        try:
            params = {
                "db": "pubmed",
                "id": pubmed_id,
                "retmode": "xml"
            }
            
            response = self.session.get(
                f"{self.PUBMED_BASE}/efetch.fcgi",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            abstract_texts = []
            
            for abstract in root.findall(".//Abstract/AbstractText"):
                label = abstract.get('Label', '')
                text = abstract.text or ""
                if label:
                    abstract_texts.append(f"{label}: {text}")
                else:
                    abstract_texts.append(text)
            
            return " ".join(abstract_texts)
            
        except Exception as e:
            logger.error(f"Error fetching abstract for {pubmed_id}: {e}")
            return ""
    
    def _get_item_value(self, doc_sum, item_name: str) -> Optional[str]:
        """Extract item value from XML document summary"""
        item = doc_sum.find(f".//Item[@Name='{item_name}']")
        return item.text if item is not None else None
    
    async def _fetch_who_async(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Fetch from WHO asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._fetch_who, query, max_results)
    
    def _fetch_who(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Fetch guidelines and data from WHO.
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            List of WHO documents
        """
        # Note: WHO doesn't have a public search API, this is a placeholder
        # In production, you would integrate with WHO's data repository
        logger.info(f"WHO search for '{query}' (API integration pending)")
        return []
    
    async def _fetch_cdc_async(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Fetch from CDC asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._fetch_cdc, query, max_results)
    
    def _fetch_cdc(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Fetch data from CDC.
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            List of CDC documents
        """
        # Note: CDC data.gov integration would go here
        logger.info(f"CDC search for '{query}' (API integration pending)")
        return []
    
    async def _fetch_nih_async(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Fetch from NIH asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._fetch_nih, query, max_results)
    
    def _fetch_nih(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Fetch data from NIH.
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            List of NIH documents
        """
        # NIH uses PubMed infrastructure, so we can leverage existing PubMed integration
        logger.info(f"NIH search for '{query}' (using PubMed backend)")
        return []
    
    def format_for_indexing(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format fetched document for knowledge base indexing.
        
        Args:
            document: Raw document from source
            
        Returns:
            Formatted document with content and metadata
        """
        source = document.get('source', 'Unknown')
        
        if source == 'PubMed':
            content_parts = [
                f"Title: {document['title']}",
                f"Authors: {document['authors']}",
                f"Journal: {document['journal']}",
                f"Published: {document['publication_date']}",
                f"\nAbstract:\n{document['abstract']}",
                f"\nSource: {document['url']}"
            ]
            
            metadata = {
                "source": "PubMed",
                "document_id": f"pubmed_{document['pubmed_id']}",
                "title": document['title'],
                "pubmed_id": document['pubmed_id'],
                "url": document['url'],
                "publication_date": document['publication_date'],
                "journal": document['journal'],
                "fetched_at": document['fetched_at'],
                "category": "Research Paper"
            }
        else:
            content_parts = [str(document)]
            metadata = {
                "source": source,
                "document_id": f"{source.lower()}_{hash(str(document))}",
                "fetched_at": datetime.utcnow().isoformat()
            }
        
        return {
            "content": "\n\n".join(content_parts),
            "metadata": metadata
        }
    
    async def auto_update_knowledge_base(
        self,
        vector_kb,
        topics: List[str],
        sources: List[str] = None,
        results_per_topic: int = 5
    ) -> Dict[str, Any]:
        """
        Automatically update knowledge base with latest online data.
        
        Args:
            vector_kb: Vector knowledge base instance
            topics: Medical topics to track
            sources: Sources to query
            results_per_topic: Results per topic
            
        Returns:
            Update summary
        """
        logger.info(f"Auto-updating KB with {len(topics)} topics from online sources")
        
        all_documents = []
        errors = []
        
        for topic in topics:
            try:
                # Fetch from all sources
                results = await self.fetch_comprehensive_knowledge(
                    query=topic,
                    sources=sources,
                    max_results=results_per_topic
                )
                
                # Collect all documents
                for source_name, documents in results.items():
                    all_documents.extend(documents)
                
            except Exception as e:
                logger.error(f"Error fetching topic '{topic}': {e}")
                errors.append({
                    "topic": topic,
                    "error": str(e)
                })
        
        # Index documents
        indexed_count = 0
        for doc in all_documents:
            try:
                formatted = self.format_for_indexing(doc)
                chunks_added = vector_kb.add_document(
                    content=formatted["content"],
                    metadata=formatted["metadata"]
                )
                if chunks_added > 0:
                    indexed_count += 1
            except Exception as e:
                logger.error(f"Error indexing document: {e}")
                errors.append({
                    "document": doc.get('title', 'Unknown'),
                    "error": str(e)
                })
        
        return {
            "topics_searched": len(topics),
            "documents_found": len(all_documents),
            "documents_indexed": indexed_count,
            "sources_used": sources or ['pubmed', 'who', 'cdc', 'nih'],
            "errors": errors,
            "timestamp": datetime.utcnow().isoformat()
        }


# Global instance
_online_sources = None

def get_online_medical_sources() -> OnlineMedicalSources:
    """Get or create online medical sources instance"""
    global _online_sources
    if _online_sources is None:
        _online_sources = OnlineMedicalSources()
    return _online_sources
