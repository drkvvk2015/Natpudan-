"""
Document Upload and Knowledge Management API Router
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import logging

from app.services.vector_knowledge_base import get_vector_knowledge_base
from app.services.document_manager import get_document_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/document")
async def upload_document(
    file: UploadFile = File(...),
    source: Optional[str] = None,
    category: Optional[str] = None,
    description: Optional[str] = None
):
    """
    Upload a medical document (PDF, DOCX, TXT) to knowledge base.
    The document will be processed, indexed, and made searchable.
    """
    try:
        # Read file content
        content = await file.read()

        # Save document
        doc_manager = get_document_manager()
        filename = file.filename or "unnamed_document"
        doc_info = await doc_manager.save_upload(
            content,
            filename,
            metadata={
                "source": source,
                "category": category,
                "description": description
            }
        )

        # Index document in vector knowledge base
        kb = get_vector_knowledge_base()
        text_content = doc_manager.get_document_text(doc_info["document_id"])

        if text_content:
            chunk_count = kb.add_document(
                content=text_content,
                metadata={
                    "document_id": doc_info["document_id"],
                    "filename": filename,
                    "source": source or "user_upload",
                    "category": category or "general",
                    "description": description
                }
            )
            doc_info["indexed_chunks"] = chunk_count
        else:
            doc_info["indexed_chunks"] = 0

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Document '{filename}' uploaded and indexed successfully",
                "document": doc_info
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/documents")
def list_documents() -> Dict[str, Any]:
    """List all uploaded documents"""
    try:
        doc_manager = get_document_manager()
        documents = doc_manager.list_documents()

        return {
            "success": True,
            "documents": documents,
            "count": len(documents)
        }
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}")
def get_document(document_id: str) -> Dict[str, Any]:
    """Get document information"""
    try:
        doc_manager = get_document_manager()
        doc_info = doc_manager.get_document(document_id)

        if doc_info is None:
            raise HTTPException(status_code=404, detail="Document not found")

        return {
            "success": True,
            "document": doc_info
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}")
def delete_document(document_id: str) -> Dict[str, Any]:
    """Delete a document and remove from knowledge base"""
    try:
        # Delete from document manager
        doc_manager = get_document_manager()
        deleted = doc_manager.delete_document(document_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Document not found")

        # Delete from vector knowledge base
        kb = get_vector_knowledge_base()
        chunks_deleted = kb.delete_document(document_id)

        return {
            "success": True,
            "message": "Document deleted successfully",
            "chunks_deleted": chunks_deleted
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))
