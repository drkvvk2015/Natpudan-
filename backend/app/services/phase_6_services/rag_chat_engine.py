"""
Phase 6 - RAG Chat Engine

Retrieval-Augmented Generation for medical knowledge base.
Combines local LLM with FAISS vector search.
"""

import logging
from typing import Optional, List, Dict, Any, AsyncGenerator
import numpy as np
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class MedicalRAGEngine:
    """
    Retrieval-Augmented Generation engine for medical queries.
    
    Integrates:
    - FAISS vector database (20,623 medical documents)
    - Local LLM (Ollama + LLaMA)
    - Medical knowledge base search
    - Context-aware response generation
    """
    
    def __init__(
        self,
        vector_db,  # FAISS DB with embeddings
        ollama_client,  # Ollama LLM client
        top_k: int = 5,
        temperature: float = 0.7
    ):
        """
        Initialize RAG engine.
        
        Args:
            vector_db: FAISS vector database instance
            ollama_client: Ollama client for LLM
            top_k: Number of documents to retrieve
            temperature: LLM temperature for responses
        """
        self.vector_db = vector_db
        self.ollama_client = ollama_client
        self.top_k = top_k
        self.temperature = temperature
        self.query_history = []
        logger.info("✓ Medical RAG Engine initialized")
    
    def _build_context(self, documents: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved documents."""
        context = "Medical Knowledge Base Context:\n"
        context += "=" * 50 + "\n\n"
        
        for i, doc in enumerate(documents, 1):
            title = doc.get("title", "Document")
            content = doc.get("content", "")[:300]  # Truncate for context window
            source = doc.get("source", "Unknown")
            
            context += f"{i}. [{title}]\n"
            context += f"   Source: {source}\n"
            context += f"   Content: {content}...\n\n"
        
        context += "=" * 50 + "\n"
        return context
    
    def _build_system_prompt(self) -> str:
        """Build medical AI system prompt."""
        return """You are a knowledgeable medical AI assistant. Your role is to:
1. Answer medical questions accurately based on the provided knowledge base context
2. Cite sources when referencing specific medical facts
3. Provide clear, understandable explanations
4. Acknowledge limitations and recommend consulting healthcare professionals for diagnosis/treatment decisions
5. Be cautious about potential drug interactions and contraindications

Always prioritize patient safety and medical accuracy."""
    
    async def search_and_retrieve(
        self,
        query: str,
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search vector DB and retrieve relevant documents.
        
        Args:
            query: Medical query
            top_k: Number of documents to retrieve
            
        Returns:
            List of relevant documents with scores
        """
        if top_k is None:
            top_k = self.top_k
        
        try:
            # Search vector DB
            if not hasattr(self.vector_db, 'search'):
                logger.warning("Vector DB search not implemented, returning empty context")
                return []
            
            results = await self.vector_db.search(query, top_k=top_k)
            
            logger.info(f"✓ Retrieved {len(results)} documents for: {query}")
            return results
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    async def generate_response(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        max_tokens: int = 1000
    ) -> str:
        """
        Generate response using LLM with retrieved context.
        
        Args:
            query: Medical question
            documents: Retrieved context documents
            max_tokens: Maximum response length
            
        Returns:
            Generated medical response
        """
        try:
            context = self._build_context(documents)
            system_prompt = self._build_system_prompt()
            
            # Build full prompt
            full_prompt = f"""{system_prompt}

{context}

User Question: {query}

Please provide a helpful and accurate medical response based on the context above."""
            
            # Generate with local LLM
            response = await self.ollama_client.generate(
                prompt=full_prompt,
                max_tokens=max_tokens,
                temperature=self.temperature
            )
            
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error generating response: {str(e)}"
    
    async def generate_response_stream(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        max_tokens: int = 1000
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming response using LLM.
        
        Args:
            query: Medical question
            documents: Retrieved context documents
            max_tokens: Maximum response length
            
        Yields:
            Response tokens one at a time
        """
        try:
            context = self._build_context(documents)
            system_prompt = self._build_system_prompt()
            
            full_prompt = f"""{system_prompt}

{context}

User Question: {query}

Please provide a helpful and accurate medical response based on the context above."""
            
            # Stream response from LLM
            async for token in self.ollama_client.generate_stream(
                prompt=full_prompt,
                max_tokens=max_tokens,
                temperature=self.temperature
            ):
                yield token
        except Exception as e:
            logger.error(f"Error in streaming: {e}")
            yield f"\n[Error: {str(e)}]"
    
    async def rag_query(
        self,
        query: str,
        include_sources: bool = True,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Complete RAG pipeline: retrieve + generate.
        
        Args:
            query: Medical question
            include_sources: Include source citations
            max_tokens: Maximum response length
            
        Returns:
            Response with sources and metadata
        """
        try:
            # 1. Retrieve
            documents = await self.search_and_retrieve(query)
            
            # 2. Generate
            response = await self.generate_response(query, documents, max_tokens)
            
            # 3. Build result
            result = {
                "status": "success",
                "query": query,
                "response": response,
                "retrieved_count": len(documents),
                "timestamp": datetime.now().isoformat()
            }
            
            if include_sources and documents:
                result["sources"] = [
                    {
                        "title": doc.get("title"),
                        "source": doc.get("source"),
                        "score": doc.get("score", 0.0)
                    }
                    for doc in documents
                ]
            
            # Track query
            self.query_history.append({
                "query": query,
                "response_length": len(response),
                "documents_retrieved": len(documents),
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"✓ RAG query complete: {len(response)} chars, {len(documents)} sources")
            
            return result
        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            return {
                "status": "error",
                "query": query,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def rag_query_stream(
        self,
        query: str,
        include_sources: bool = True,
        max_tokens: int = 1000
    ) -> AsyncGenerator[str, None]:
        """
        Stream complete RAG response (retrieve + stream generate).
        
        Args:
            query: Medical question
            include_sources: Include sources in response
            max_tokens: Maximum response length
            
        Yields:
            JSON-serialized chunks with token updates
        """
        try:
            # 1. Retrieve documents upfront
            documents = await self.search_and_retrieve(query)
            
            # 2. Send metadata first
            metadata = {
                "type": "metadata",
                "query": query,
                "retrieved_count": len(documents),
                "timestamp": datetime.now().isoformat()
            }
            
            if include_sources and documents:
                metadata["sources"] = [
                    {
                        "title": doc.get("title"),
                        "source": doc.get("source"),
                        "score": doc.get("score", 0.0)
                    }
                    for doc in documents
                ]
            
            yield json.dumps(metadata) + "\n"
            
            # 3. Stream response
            full_response = ""
            async for token in self.generate_response_stream(query, documents, max_tokens):
                full_response += token
                
                # Send token update
                token_msg = {
                    "type": "token",
                    "content": token,
                    "length": len(full_response)
                }
                yield json.dumps(token_msg) + "\n"
            
            # 4. Send completion
            completion = {
                "type": "complete",
                "total_length": len(full_response),
                "timestamp": datetime.now().isoformat()
            }
            yield json.dumps(completion) + "\n"
            
            # Track query
            self.query_history.append({
                "query": query,
                "response_length": len(full_response),
                "documents_retrieved": len(documents),
                "streaming": True,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error in streaming RAG query: {e}")
            error_msg = {
                "type": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            yield json.dumps(error_msg) + "\n"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get RAG engine statistics."""
        return {
            "total_queries": len(self.query_history),
            "average_response_length": np.mean([
                h.get("response_length", 0) for h in self.query_history
            ]) if self.query_history else 0,
            "total_documents_retrieved": sum(
                h.get("documents_retrieved", 0) for h in self.query_history
            ),
            "configuration": {
                "top_k": self.top_k,
                "temperature": self.temperature
            }
        }


# Singleton instance
_rag_engine: Optional[MedicalRAGEngine] = None


async def get_rag_engine(
    vector_db=None,
    ollama_client=None,
    top_k: int = 5
) -> MedicalRAGEngine:
    """Get or create RAG engine."""
    global _rag_engine
    
    if _rag_engine is None:
        if vector_db is None or ollama_client is None:
            logger.warning("RAG engine initialization incomplete - missing dependencies")
            return None
        
        _rag_engine = MedicalRAGEngine(vector_db, ollama_client, top_k)
    
    return _rag_engine
