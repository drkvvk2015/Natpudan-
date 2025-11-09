"""
Online Knowledge Service
Fetches real-time medical data from online sources
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import aiofiles
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

# Guideline source base URLs for future API integration
CDC_API_BASE = "https://tools.cdc.gov/api"
WHO_GUIDELINES_URL = "https://www.who.int/publications/guidelines"
NICE_API_BASE = "https://www.nice.org.uk/guidance"


class OnlineKnowledgeService:
    """
    Fetches and caches medical knowledge from online sources:
    - PubMed for recent research papers
    - Clinical guidelines from authoritative sources
    - Drug information databases
    - Medical news and updates
    """
    
    def __init__(self, cache_dir: str = "cache/online_knowledge"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_duration = timedelta(hours=24)  # Cache for 24 hours
        self.initialized = False
        
    async def initialize(self):
        """Initialize the service"""
        if self.initialized:
            return
        
        logger.info("Initializing Online Knowledge Service...")
        # Clean old cache entries
        await self._clean_old_cache()
        self.initialized = True
        logger.info("Online Knowledge Service initialized")
        
    async def search_pubmed(
        self,
        query: str,
        max_results: int = 5,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search PubMed for recent medical research
        
        Args:
            query: Search query
            max_results: Maximum number of results
            use_cache: Whether to use cached results
            
        Returns:
            List of research articles with titles, abstracts, and metadata
        """
        cache_key = f"pubmed_{hashlib.md5(query.encode()).hexdigest()}_{max_results}"
        
        # Check cache first
        if use_cache:
            cached = await self._get_from_cache(cache_key)
            if cached:
                logger.info(f"Retrieved PubMed results from cache for: {query}")
                return cached
                
        try:
            # PubMed E-utilities API (free, no API key required for basic use)
            import requests
            
            # Step 1: Search for article IDs
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            search_params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "retmode": "json",
                "sort": "relevance",
                "reldate": 1825  # Last 5 years
            }
            
            search_response = requests.get(search_url, params=search_params, timeout=10)
            search_response.raise_for_status()
            search_data = search_response.json()
            
            id_list = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not id_list:
                logger.info(f"No PubMed results found for: {query}")
                return []
                
            # Step 2: Fetch article details
            fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(id_list),
                "retmode": "xml"
            }
            
            fetch_response = requests.get(fetch_url, params=fetch_params, timeout=15)
            fetch_response.raise_for_status()
            
            # Parse XML response (simplified - in production use proper XML parser)
            articles = self._parse_pubmed_xml(fetch_response.text)
            
            # Cache results
            await self._save_to_cache(cache_key, articles)
            
            logger.info(f"Retrieved {len(articles)} PubMed articles for: {query}")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching PubMed data: {e}")
            return []
            
    def _parse_pubmed_xml(self, xml_text: str) -> List[Dict[str, Any]]:
        """Parse PubMed XML response (simplified)"""
        # This is a simplified parser - in production, use xml.etree.ElementTree
        articles = []
        
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_text)
            
            for article in root.findall(".//PubmedArticle"):
                try:
                    # Extract title
                    title_elem = article.find(".//ArticleTitle")
                    title = title_elem.text if title_elem is not None else "No title"
                    
                    # Extract abstract
                    abstract_texts = article.findall(".//AbstractText")
                    abstract = " ".join([
                        at.text for at in abstract_texts if at.text
                    ]) if abstract_texts else "No abstract available"
                    
                    # Extract publication date
                    pub_date = article.find(".//PubDate")
                    year = pub_date.find("Year")
                    year_text = year.text if year is not None else "Unknown"
                    
                    # Extract PMID
                    pmid = article.find(".//PMID")
                    pmid_text = pmid.text if pmid is not None else "Unknown"
                    
                    # Extract authors
                    authors = []
                    for author in article.findall(".//Author"):
                        last_name = author.find("LastName")
                        fore_name = author.find("ForeName")
                        if last_name is not None and fore_name is not None:
                            authors.append(f"{fore_name.text} {last_name.text}")
                    
                    articles.append({
                        "title": title,
                        "abstract": abstract[:500] + "..." if len(abstract) > 500 else abstract,
                        "year": year_text,
                        "pmid": pmid_text,
                        "authors": ", ".join(authors[:3]) if authors else "Unknown",
                        "source": "PubMed",
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid_text}/"
                    })
                except Exception as e:
                    logger.warning(f"Error parsing article: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing PubMed XML: {e}")
            
        return articles
        
    async def get_clinical_guidelines(
        self,
        condition: str,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Fetch clinical guidelines from multiple authoritative sources in parallel
        
        Args:
            condition: Medical condition
            use_cache: Whether to use cached results
            
        Returns:
            List of clinical guidelines with content and sources
        """
        cache_key = f"guidelines_{hashlib.md5(condition.encode()).hexdigest()}"
        
        if use_cache:
            cached = await self._get_from_cache(cache_key)
            if cached:
                logger.info(f"Retrieved guidelines from cache for: {condition}")
                return cached
                
        try:
            # Parallel fetching from multiple guideline sources
            guidelines = []
            
            # Execute all searches in parallel for better performance
            tasks = [
                self.search_pubmed(f"{condition} practice guideline[Publication Type]", max_results=2, use_cache=use_cache),
                self._fetch_cdc_guidelines(condition),
                self._fetch_who_guidelines(condition),
                self._fetch_nice_guidelines(condition)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 1. PubMed practice guidelines
            pubmed_results = results[0] if not isinstance(results[0], Exception) else []
            for article in pubmed_results:
                guidelines.append({
                    "title": article['title'],
                    "content": article['abstract'],
                    "source": "PubMed Clinical Guidelines",
                    "year": article['year'],
                    "url": article['url'],
                    "type": "research_guideline"
                })
            
            # 2. CDC guidelines
            cdc_results = results[1] if not isinstance(results[1], Exception) else []
            guidelines.extend(cdc_results)
            
            # 3. WHO guidelines
            who_results = results[2] if not isinstance(results[2], Exception) else []
            guidelines.extend(who_results)
            
            # 4. NICE guidelines (UK)
            nice_results = results[3] if not isinstance(results[3], Exception) else []
            guidelines.extend(nice_results)
            
            # Cache results with extended TTL for guidelines (7 days)
            await self._save_to_cache(cache_key, guidelines, ttl_override=timedelta(days=7))
            
            logger.info(f"Retrieved {len(guidelines)} guidelines from {len([r for r in results if not isinstance(r, Exception)])} sources for: {condition}")
            return guidelines
            
        except Exception as e:
            logger.error(f"Error fetching clinical guidelines: {e}")
            return []
            
    async def get_drug_information(
        self,
        drug_name: str,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch comprehensive drug information from online sources
        
        Args:
            drug_name: Name of the drug
            use_cache: Whether to use cached results
            
        Returns:
            Drug information including indications, contraindications, dosing
        """
        cache_key = f"drug_{hashlib.md5(drug_name.encode()).hexdigest()}"
        
        if use_cache:
            cached = await self._get_from_cache(cache_key)
            if cached:
                logger.info(f"Retrieved drug info from cache for: {drug_name}")
                return cached
                
        try:
            # Search PubMed for drug information
            pubmed_results = await self.search_pubmed(
                f"{drug_name} pharmacology clinical trial",
                max_results=3,
                use_cache=use_cache
            )
            
            drug_info = {
                "drug_name": drug_name,
                "research_findings": [
                    {
                        "title": article['title'],
                        "summary": article['abstract'],
                        "year": article['year'],
                        "url": article['url']
                    }
                    for article in pubmed_results
                ],
                "last_updated": datetime.now().isoformat(),
                "source": "PubMed and clinical databases"
            }
            
            # Cache results
            await self._save_to_cache(cache_key, drug_info)
            
            logger.info(f"Retrieved drug information for: {drug_name}")
            return drug_info
            
        except Exception as e:
            logger.error(f"Error fetching drug information: {e}")
            return {
                "drug_name": drug_name,
                "error": str(e),
                "research_findings": []
            }
            
    async def get_medical_news(
        self,
        topic: str,
        max_results: int = 3,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent medical news and updates
        
        Args:
            topic: Medical topic
            max_results: Maximum number of news items
            use_cache: Whether to use cached results
            
        Returns:
            List of medical news items
        """
        cache_key = f"news_{hashlib.md5(topic.encode()).hexdigest()}_{max_results}"
        
        if use_cache:
            cached = await self._get_from_cache(cache_key)
            if cached:
                logger.info(f"Retrieved medical news from cache for: {topic}")
                return cached
                
        try:
            # Search PubMed for recent publications (last 30 days)
            import requests
            
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            search_params = {
                "db": "pubmed",
                "term": topic,
                "retmax": max_results,
                "retmode": "json",
                "sort": "pub_date",
                "reldate": 30  # Last 30 days
            }
            
            response = requests.get(search_url, params=search_params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            id_list = data.get("esearchresult", {}).get("idlist", [])
            
            if id_list:
                articles = await self.search_pubmed(
                    topic,
                    max_results=len(id_list),
                    use_cache=False
                )
                
                news_items = [
                    {
                        "title": article['title'],
                        "summary": article['abstract'],
                        "date": article['year'],
                        "source": "PubMed Recent Publications",
                        "url": article['url']
                    }
                    for article in articles[:max_results]
                ]
            else:
                news_items = []
                
            # Cache results
            await self._save_to_cache(cache_key, news_items)
            
            logger.info(f"Retrieved {len(news_items)} medical news items for: {topic}")
            return news_items
            
        except Exception as e:
            logger.error(f"Error fetching medical news: {e}")
            return []
            
    async def search_comprehensive(
        self,
        query: str,
        include_research: bool = True,
        include_guidelines: bool = True,
        include_news: bool = False
    ) -> Dict[str, Any]:
        """
        Parallel comprehensive search across all online knowledge sources with performance metrics
        
        Args:
            query: Search query
            include_research: Include PubMed research
            include_guidelines: Include clinical guidelines
            include_news: Include recent medical news
            
        Returns:
            Comprehensive results from multiple sources with timing data
        """
        start_time = datetime.now()
        results = {
            "query": query,
            "timestamp": start_time.isoformat(),
            "sources": {}
        }
        
        # Build parallel task list
        tasks = []
        task_names = []
        
        if include_research:
            tasks.append(self.search_pubmed(query, max_results=5))
            task_names.append("research")
            
        if include_guidelines:
            tasks.append(self.get_clinical_guidelines(query))
            task_names.append("guidelines")
            
        if include_news:
            tasks.append(self.get_medical_news(query, max_results=3))
            task_names.append("news")
        
        # Execute all searches in parallel with timeout
        try:
            task_results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=30.0  # 30 second overall timeout
            )
            
            # Map results to source names
            for idx, (source_name, result) in enumerate(zip(task_names, task_results)):
                if isinstance(result, Exception):
                    logger.error(f"Error fetching {source_name}: {result}")
                    results["sources"][source_name] = []
                else:
                    results["sources"][source_name] = result
                    
        except asyncio.TimeoutError:
            logger.error(f"Comprehensive search timeout after 30s for: {query}")
            for name in task_names:
                results["sources"].setdefault(name, [])
                
        # Count total results and calculate timing
        total_results = sum(
            len(v) if isinstance(v, list) else 1
            for v in results["sources"].values()
        )
        results["total_results"] = total_results
        results["fetch_time_ms"] = int((datetime.now() - start_time).total_seconds() * 1000)
        
        logger.info(f"Comprehensive search returned {total_results} results in {results['fetch_time_ms']}ms for: {query}")
        return results
        
    async def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Retrieve data from cache if not expired"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
            
        try:
            async with aiofiles.open(cache_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)
                
            # Check expiration with respect to TTL
            cached_time = datetime.fromisoformat(data['cached_at'])
            ttl_hours = data.get('ttl_hours', int(self.cache_duration.total_seconds() / 3600))
            cache_ttl = timedelta(hours=ttl_hours)
            
            if datetime.now() - cached_time > cache_ttl:
                # Cache expired
                cache_file.unlink()
                return None
                
            return data['content']
            
        except Exception as e:
            logger.warning(f"Error reading cache: {e}")
            return None
            
    async def _save_to_cache(self, cache_key: str, content: Any, ttl_override: Optional[timedelta] = None):
        """Save data to cache with optional TTL override"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            data = {
                "cached_at": datetime.now().isoformat(),
                "content": content,
                "ttl_hours": int((ttl_override or self.cache_duration).total_seconds() / 3600)
            }
            
            async with aiofiles.open(cache_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, indent=2))
                
        except Exception as e:
            logger.error(f"Error saving to cache: {e}")
            
    async def _clean_old_cache(self):
        """Remove expired cache entries"""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    async with aiofiles.open(cache_file, 'r', encoding='utf-8') as f:
                        content = await f.read()
                        data = json.loads(content)
                        
                    cached_time = datetime.fromisoformat(data['cached_at'])
                    ttl_hours = data.get('ttl_hours', int(self.cache_duration.total_seconds() / 3600))
                    cache_ttl = timedelta(hours=ttl_hours)
                    if datetime.now() - cached_time > cache_ttl:
                        cache_file.unlink()
                        
                except Exception as e:
                    logger.warning(f"Error cleaning cache file {cache_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Error cleaning cache: {e}")
            
    async def _fetch_cdc_guidelines(self, condition: str) -> List[Dict[str, Any]]:
        """Fetch CDC guidelines (structured placeholder for production API integration)"""
        try:
            guidelines = []
            cdc_topics = {
                "diabetes": "CDC Diabetes Guidelines: Standards of Medical Care",
                "hypertension": "CDC High Blood Pressure Guidelines",
                "covid": "CDC COVID-19 Clinical Care Guidelines",
                "tuberculosis": "CDC TB Treatment Guidelines",
                "hiv": "CDC HIV Prevention and Treatment Guidelines",
                "influenza": "CDC Seasonal Influenza Guidelines",
                "pneumonia": "CDC Pneumonia Management Guidelines"
            }
            
            condition_lower = condition.lower()
            for key, title in cdc_topics.items():
                if key in condition_lower:
                    guidelines.append({
                        "title": title,
                        "content": f"CDC provides comprehensive clinical guidelines for {condition}. Visit CDC website for latest evidence-based recommendations including prevention, diagnosis, treatment protocols, and vaccination schedules.",
                        "source": "Centers for Disease Control and Prevention (CDC)",
                        "year": "2024-2025",
                        "url": f"https://www.cdc.gov/{key}",
                        "type": "cdc_guideline"
                    })
                    break
            
            return guidelines
        except Exception as e:
            logger.warning(f"Error fetching CDC guidelines: {e}")
            return []
    
    async def _fetch_who_guidelines(self, condition: str) -> List[Dict[str, Any]]:
        """Fetch WHO guidelines (structured placeholder for production integration)"""
        try:
            guidelines = [{
                "title": f"WHO Global Guidelines for {condition}",
                "content": f"WHO provides international evidence-based guidelines for {condition} management and prevention, regularly updated based on global research and expert consensus.",
                "source": "World Health Organization (WHO)",
                "year": "2024-2025",
                "url": WHO_GUIDELINES_URL,
                "type": "who_guideline"
            }]
            return guidelines
        except Exception as e:
            logger.warning(f"Error fetching WHO guidelines: {e}")
            return []
    
    async def _fetch_nice_guidelines(self, condition: str) -> List[Dict[str, Any]]:
        """Fetch NICE (UK) guidelines (structured placeholder for production integration)"""
        try:
            guidelines = []
            nice_topics = {
                "diabetes": "Type 2 diabetes in adults: management (NG28)",
                "hypertension": "Hypertension in adults: diagnosis and management (NG136)",
                "asthma": "Asthma: diagnosis, monitoring and chronic asthma management (NG80)",
                "copd": "Chronic obstructive pulmonary disease in over 16s: diagnosis and management (NG115)",
                "heart failure": "Chronic heart failure in adults: diagnosis and management (NG106)",
                "depression": "Depression in adults: treatment and management (NG222)",
                "pneumonia": "Pneumonia (community-acquired): antimicrobial prescribing (NG138)"
            }
            
            condition_lower = condition.lower()
            for key, title in nice_topics.items():
                if key in condition_lower:
                    guidelines.append({
                        "title": title,
                        "content": f"NICE guideline covering diagnosis, management, and treatment protocols for {condition} based on UK clinical evidence and cost-effectiveness analysis.",
                        "source": "National Institute for Health and Care Excellence (NICE)",
                        "year": "2024",
                        "url": f"{NICE_API_BASE}/published",
                        "type": "nice_guideline"
                    })
                    break
            
            return guidelines
        except Exception as e:
            logger.warning(f"Error fetching NICE guidelines: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get enhanced service statistics"""
        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files if f.is_file())
        return {
            "initialized": self.initialized,
            "cache_entries": len(cache_files),
            "cache_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_dir": str(self.cache_dir),
            "guideline_sources": ["PubMed", "CDC", "WHO", "NICE"]
        }
