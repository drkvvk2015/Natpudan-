"""
Natpudan AI Medical Assistant - Backend API
FastAPI server for medical AI assistant functionality.
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

from pdf_utils import extract_text_from_pdf_bytes, clean_medical_text, chunk_text
from knowledge_base import KnowledgeBase
from ai_service import AIService

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Natpudan AI Medical Assistant",
    description="AI-powered medical assistant for physicians",
    version="1.0.0"
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
knowledge_base = KnowledgeBase()
ai_service = AIService()


# Pydantic models for request/response
class SymptomAnalysisRequest(BaseModel):
    symptoms: str
    age: Optional[int] = None
    gender: Optional[str] = None


class DrugInteractionRequest(BaseModel):
    medications: List[str]


class MedicalSearchRequest(BaseModel):
    query: str


class TreatmentRequest(BaseModel):
    condition: str
    patient_info: dict


class QuestionRequest(BaseModel):
    question: str


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Natpudan AI Medical Assistant API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file and extract medical knowledge.
    
    Args:
        file: PDF file upload
        
    Returns:
        Success message with document ID
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Read file content
        content = await file.read()
        
        # Extract text from PDF
        text = extract_text_from_pdf_bytes(content)
        
        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        # Clean the text
        cleaned_text = clean_medical_text(text)
        
        # Store in knowledge base
        knowledge_base.add_document(
            filename=file.filename,
            content=cleaned_text,
            metadata={
                "size": len(content),
                "pages": text.count('\f') + 1
            }
        )
        
        return {
            "success": True,
            "message": f"Successfully processed {file.filename}",
            "filename": file.filename,
            "text_length": len(cleaned_text)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/api/analyze-symptoms")
async def analyze_symptoms(request: SymptomAnalysisRequest):
    """
    Analyze patient symptoms using AI.
    
    Args:
        request: Symptom analysis request
        
    Returns:
        AI-generated analysis
    """
    try:
        # Search knowledge base for relevant context
        kb_results = knowledge_base.search_knowledge(request.symptoms, max_results=2)
        context = "\n\n".join([result["document"]["content"][:500] for result in kb_results])
        
        # Get AI analysis
        analysis = ai_service.analyze_symptoms(
            symptoms=request.symptoms,
            age=request.age,
            gender=request.gender,
            context=context if context else None
        )
        
        return {
            "success": True,
            "analysis": analysis,
            "sources_used": len(kb_results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing symptoms: {str(e)}")


@app.post("/api/check-interactions")
async def check_interactions(request: DrugInteractionRequest):
    """
    Check for drug interactions.
    
    Args:
        request: Drug interaction request
        
    Returns:
        AI-generated interaction analysis
    """
    try:
        if len(request.medications) < 2:
            raise HTTPException(status_code=400, detail="At least 2 medications required")
        
        # Search knowledge base for drug information
        query = " ".join(request.medications)
        kb_results = knowledge_base.search_knowledge(query, max_results=2)
        context = "\n\n".join([result["document"]["content"][:500] for result in kb_results])
        
        # Get AI analysis
        analysis = ai_service.check_drug_interactions(
            medications=request.medications,
            context=context if context else None
        )
        
        return {
            "success": True,
            "analysis": analysis,
            "sources_used": len(kb_results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking interactions: {str(e)}")


@app.post("/api/search-medical-info")
async def search_medical_info(request: MedicalSearchRequest):
    """
    Search for medical information.
    
    Args:
        request: Medical search request
        
    Returns:
        AI-generated medical information
    """
    try:
        # Search knowledge base
        kb_results = knowledge_base.search_knowledge(request.query, max_results=3)
        context = "\n\n".join([result["document"]["content"][:500] for result in kb_results])
        
        # Get AI response
        info = ai_service.search_medical_information(
            query=request.query,
            context=context if context else None
        )
        
        return {
            "success": True,
            "information": info,
            "sources_used": len(kb_results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching medical info: {str(e)}")


@app.post("/api/treatment-suggestions")
async def treatment_suggestions(request: TreatmentRequest):
    """
    Generate treatment suggestions.
    
    Args:
        request: Treatment request
        
    Returns:
        AI-generated treatment suggestions
    """
    try:
        # Search knowledge base for treatment information
        kb_results = knowledge_base.search_knowledge(request.condition, max_results=2)
        context = "\n\n".join([result["document"]["content"][:500] for result in kb_results])
        
        # Get AI suggestions
        suggestions = ai_service.generate_treatment_suggestions(
            condition=request.condition,
            patient_info=request.patient_info,
            context=context if context else None
        )
        
        return {
            "success": True,
            "suggestions": suggestions,
            "sources_used": len(kb_results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating treatment suggestions: {str(e)}")


@app.post("/api/ask-question")
async def ask_question(request: QuestionRequest):
    """
    Ask a general medical question.
    
    Args:
        request: Question request
        
    Returns:
        AI-generated answer
    """
    try:
        # Search knowledge base
        kb_results = knowledge_base.search_knowledge(request.question, max_results=3)
        context = "\n\n".join([result["document"]["content"][:500] for result in kb_results])
        
        # Get AI response using medical search
        answer = ai_service.search_medical_information(
            query=request.question,
            context=context if context else None
        )
        
        return {
            "success": True,
            "answer": answer,
            "sources_used": len(kb_results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error answering question: {str(e)}")


@app.get("/api/knowledge-base/stats")
async def get_kb_stats():
    """Get knowledge base statistics."""
    try:
        stats = knowledge_base.get_statistics()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@app.get("/api/knowledge-base/documents")
async def get_documents():
    """Get all documents in the knowledge base."""
    try:
        docs = knowledge_base.get_all_documents()
        # Return simplified version without full content
        simplified_docs = [
            {
                "id": doc["id"],
                "filename": doc["filename"],
                "timestamp": doc["timestamp"],
                "content_length": len(doc["content"]),
                "metadata": doc.get("metadata", {})
            }
            for doc in docs
        ]
        return {
            "success": True,
            "documents": simplified_docs,
            "total": len(simplified_docs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting documents: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)
