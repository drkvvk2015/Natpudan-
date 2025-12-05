"""
RAG (Retrieval-Augmented Generation) Service
Combines knowledge base retrieval with GPT-4 generation for accurate, cited responses
"""

import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    logger.warning("OpenAI not available")
    OPENAI_AVAILABLE = False


class RAGService:
    """
    Retrieval-Augmented Generation service.
    Retrieves relevant documents and uses them as context for GPT-4 responses.
    """
    
    def __init__(
        self,
        model: str = "gpt-4o",
        max_context_chunks: int = 5
    ):
        """
        Initialize RAG service.
        
        Args:
            model: OpenAI model to use
            max_context_chunks: Maximum number of document chunks to include
        """
        self.model = model
        self.max_context_chunks = max_context_chunks
        
        # Initialize OpenAI client
        self.client = None
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
        
        logger.info(f"RAG service initialized with model: {model}")
    
    def generate_with_context(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        include_citations: bool = True
    ) -> Dict[str, Any]:
        """
        Generate response using retrieved documents as context.
        
        Args:
            query: User query
            retrieved_docs: Documents from knowledge base
            system_prompt: Optional system prompt override
            include_citations: Whether to include source citations
            
        Returns:
            Generated response with citations
        """
        if not self.client:
            return {
                "error": "OpenAI client not available",
                "response": "Unable to generate response without OpenAI API key"
            }
        
        # Limit context
        context_docs = retrieved_docs[:self.max_context_chunks]
        
        # Build context string
        context_parts = []
        for i, doc in enumerate(context_docs, 1):
            content = doc.get('content', '')
            metadata = doc.get('metadata', {})
            filename = metadata.get('filename', f'Document {i}')
            
            context_parts.append(f"[Source {i}: {filename}]\n{content}\n")
        
        context = "\n---\n\n".join(context_parts)
        
        # Default system prompt
        if system_prompt is None:
            system_prompt = """You are a medical AI assistant with access to a comprehensive medical knowledge base.
Your responses should be:
1. Accurate and based on provided sources
2. Clear and easy to understand
3. Include citations when referencing specific information
4. Acknowledge limitations when information is not in the sources

Format citations as [Source X] where X is the source number."""
        
        # Build messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""Based on the following medical information sources, please answer the question.

SOURCES:
{context}

QUESTION: {query}

Please provide a comprehensive answer with citations."""}
        ]
        
        try:
            # Generate response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Lower temperature for more factual responses
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            
            # Build response
            result = {
                "query": query,
                "answer": answer,
                "model": self.model,
                "sources_used": len(context_docs),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add source citations if requested
            if include_citations:
                sources = []
                for i, doc in enumerate(context_docs, 1):
                    metadata = doc.get('metadata', {})
                    sources.append({
                        "source_number": i,
                        "filename": metadata.get('filename', 'Unknown'),
                        "document_id": metadata.get('document_id'),
                        "similarity_score": doc.get('similarity_score', 0),
                        "snippet": doc.get('content', '')[:200] + "..."
                    })
                result["sources"] = sources
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating RAG response: {e}")
            return {
                "error": str(e),
                "query": query,
                "answer": "Unable to generate response due to an error"
            }
    
    def generate_medical_summary(
        self,
        patient_data: Dict[str, Any],
        retrieved_guidelines: List[Dict[str, Any]]
    ) -> str:
        """
        Generate clinical summary based on patient data and guidelines.
        
        Args:
            patient_data: Patient information
            retrieved_guidelines: Relevant clinical guidelines
            
        Returns:
            Generated summary
        """
        if not self.client:
            return "OpenAI client not available"
        
        # Extract patient info
        symptoms = patient_data.get('symptoms', [])
        diagnosis = patient_data.get('diagnosis', 'Unknown')
        history = patient_data.get('medical_history', '')
        
        # Build context from guidelines
        context = "\n\n".join([
            doc.get('content', '')
            for doc in retrieved_guidelines[:3]
        ])
        
        # Generate summary
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a medical AI assistant. Generate concise clinical summaries based on patient data and guidelines."
                    },
                    {
                        "role": "user",
                        "content": f"""Generate a clinical summary for:

DIAGNOSIS: {diagnosis}
SYMPTOMS: {', '.join(symptoms)}
MEDICAL HISTORY: {history}

RELEVANT GUIDELINES:
{context}

Provide a concise summary with:
1. Assessment
2. Recommended treatment approach
3. Monitoring recommendations
4. Patient education points"""
                    }
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Error generating summary: {str(e)}"
    
    def extract_key_information(
        self,
        medical_text: str,
        extraction_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Extract structured information from medical text.
        
        Args:
            medical_text: Medical document text
            extraction_type: Type of extraction (general, diagnosis, treatment, etc.)
            
        Returns:
            Extracted structured data
        """
        if not self.client:
            return {"error": "OpenAI client not available"}
        
        extraction_prompts = {
            "general": "Extract key medical information including diagnoses, medications, procedures, and vital signs.",
            "diagnosis": "Extract all diagnoses mentioned, including ICD codes if present.",
            "medications": "Extract all medications with dosages, frequencies, and routes.",
            "procedures": "Extract all medical procedures, surgeries, or interventions mentioned.",
            "vitals": "Extract all vital signs including blood pressure, heart rate, temperature, etc."
        }
        
        prompt = extraction_prompts.get(extraction_type, extraction_prompts["general"])
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a medical information extraction assistant. {prompt} Return structured JSON."
                    },
                    {
                        "role": "user",
                        "content": f"Extract information from:\n\n{medical_text}"
                    }
                ],
                temperature=0.1,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            import json
            extracted = json.loads(response.choices[0].message.content)
            return extracted
            
        except Exception as e:
            logger.error(f"Error extracting information: {e}")
            return {"error": str(e)}


# Global instance
_rag_service = None

def get_rag_service() -> RAGService:
    """Get or create RAG service instance"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
