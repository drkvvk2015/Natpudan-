"""
Medical knowledge base management.
Stores and retrieves medical knowledge from uploaded PDFs and other sources.
"""
import json
import os
from typing import List, Dict, Optional
from datetime import datetime


class KnowledgeBase:
    """Manages medical knowledge storage and retrieval."""
    
    def __init__(self, storage_path: str = "knowledge_base.json"):
        """
        Initialize the knowledge base.
        
        Args:
            storage_path: Path to the JSON file for storing knowledge
        """
        self.storage_path = storage_path
        self.knowledge = self._load_knowledge()
    
    def _load_knowledge(self) -> Dict:
        """Load knowledge from storage file."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading knowledge base: {e}")
                return {"documents": [], "metadata": {}}
        return {"documents": [], "metadata": {}}
    
    def _save_knowledge(self):
        """Save knowledge to storage file."""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving knowledge base: {e}")
    
    def add_document(self, filename: str, content: str, metadata: Optional[Dict] = None):
        """
        Add a document to the knowledge base.
        
        Args:
            filename: Name of the document
            content: Text content of the document
            metadata: Optional metadata about the document
        """
        document = {
            "id": len(self.knowledge["documents"]),
            "filename": filename,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.knowledge["documents"].append(document)
        self._save_knowledge()
    
    def search_knowledge(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search the knowledge base for relevant information.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of relevant documents with similarity scores
        """
        query_lower = query.lower()
        results = []
        
        for doc in self.knowledge["documents"]:
            content_lower = doc["content"].lower()
            
            # Simple keyword matching (can be enhanced with embeddings)
            score = 0
            query_words = query_lower.split()
            
            for word in query_words:
                if word in content_lower:
                    score += content_lower.count(word)
            
            if score > 0:
                results.append({
                    "document": doc,
                    "score": score
                })
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:max_results]
    
    def get_all_documents(self) -> List[Dict]:
        """Get all documents in the knowledge base."""
        return self.knowledge["documents"]
    
    def get_document_by_id(self, doc_id: int) -> Optional[Dict]:
        """Get a specific document by ID."""
        for doc in self.knowledge["documents"]:
            if doc["id"] == doc_id:
                return doc
        return None
    
    def delete_document(self, doc_id: int) -> bool:
        """
        Delete a document from the knowledge base.
        
        Args:
            doc_id: ID of the document to delete
            
        Returns:
            True if deleted, False if not found
        """
        for i, doc in enumerate(self.knowledge["documents"]):
            if doc["id"] == doc_id:
                self.knowledge["documents"].pop(i)
                self._save_knowledge()
                return True
        return False
    
    def get_statistics(self) -> Dict:
        """Get statistics about the knowledge base."""
        return {
            "total_documents": len(self.knowledge["documents"]),
            "total_size": sum(len(doc["content"]) for doc in self.knowledge["documents"]),
            "last_updated": max(
                (doc["timestamp"] for doc in self.knowledge["documents"]),
                default=None
            )
        }
