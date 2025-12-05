"""
Knowledge Base API - PDF Upload, Processing, and Management
Supports: Multiple PDF uploads, Full text extraction, Intelligent chunking
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import os
import logging
from pathlib import Path
import shutil
from datetime import datetime

from app.services.enhanced_knowledge_base import get_knowledge_base
from app.services.local_vector_kb import get_local_knowledge_base
from app.api.auth_new import get_current_user
from app.models import User, KnowledgeDocument
from app.database import get_db
from sqlalchemy.orm import Session
import hashlib
import uuid
from app.services.online_knowledge_service import OnlineKnowledgeService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["knowledge-base"])

@router.get("/test")
async def test_kb():
    """Test endpoint to verify KB router is working"""
    logger.info("TEST ENDPOINT CALLED")
    return {"status": "test", "message": "KB router is working!"}

# Constants
MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB per file (increased for large medical textbooks)
MAX_TOTAL_SIZE = 5 * 1024 * 1024 * 1024  # 5GB total
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".doc", ".docx"}
UPLOAD_DIR = Path("data/knowledge_base/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Import large PDF processor
from app.services.large_pdf_processor import get_large_pdf_processor
from app.services.error_corrector import get_error_corrector, with_auto_correction


class PDFProcessingRequest(BaseModel):
    use_full_content: bool = False  # False = intelligent chunking (DEFAULT), True = full PDF
    chunk_size: int = 2000  # Characters per chunk (larger = fewer chunks = faster)
    overlap: int = 50  # Overlap between chunks (smaller = fewer chunks)
    extract_tables: bool = False  # Set to True if you need tables (slower)
    extract_images: bool = False
    ocr_enabled: bool = False


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    min_score: float = 0.0


@router.post("/upload")
async def upload_pdfs(
    files: List[UploadFile] = File(...),
    use_full_content: bool = False,  # Default to chunking for semantic search
    chunk_size: int = 1000,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload multiple PDF files to knowledge base.
    
    - **files**: List of PDF files (up to 200MB each, 1GB total)
    - **use_full_content**: If False (default), intelligent chunking; if True, full PDF as single document
    - **chunk_size**: Size of text chunks when use_full_content=False
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Validate file count
    if len(files) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 files allowed per upload")
    
    # Validate file types and sizes
    total_size = 0
    for file in files:
        # Check extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} has unsupported type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Read file to check size
        content = await file.read()
        file_size = len(content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} exceeds maximum size of {MAX_FILE_SIZE / 1024 / 1024:.0f}MB"
            )
        
        total_size += file_size
        
        # Reset file pointer
        await file.seek(0)
    
    if total_size > MAX_TOTAL_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Total upload size ({total_size / 1024 / 1024:.2f}MB) exceeds maximum of {MAX_TOTAL_SIZE / 1024 / 1024 / 1024:.1f}GB"
        )
    
    # Process files
    results = []
    knowledge_base = get_knowledge_base()
    
    for file in files:
        try:
            logger.info(f"Processing file: {file.filename}")
            
            # Save file temporarily
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{timestamp}_{file.filename}"
            file_path = UPLOAD_DIR / safe_filename
            
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Calculate file hash for deduplication
            file_hash = hashlib.sha256(content).hexdigest()
            
            # Check if document already exists
            existing_doc = db.query(KnowledgeDocument).filter(
                KnowledgeDocument.file_hash == file_hash
            ).first()
            
            if existing_doc:
                logger.info(f"Document {file.filename} already exists (hash: {file_hash})")
                results.append({
                    "filename": file.filename,
                    "status": "skipped",
                    "reason": "Document already uploaded",
                    "existing_document_id": existing_doc.document_id,
                    "uploaded_at": existing_doc.uploaded_at.isoformat()
                })
                continue
            
            # Extract text based on file type
            file_ext = Path(file.filename).suffix.lower()
            
            if file_ext == ".pdf":
                text_content = await extract_pdf_text(file_path, use_full_content)
            elif file_ext == ".txt":
                text_content = content.decode('utf-8', errors='ignore')
            elif file_ext in [".doc", ".docx"]:
                text_content = await extract_word_text(file_path)
            else:
                text_content = ""
            
            if not text_content.strip():
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "error": "No text content extracted",
                    "chunks": 0,
                    "characters": 0
                })
                continue
            
            # Generate unique document ID
            doc_uuid = str(uuid.uuid4())
            
            # Process content
            if use_full_content:
                # Add as single document
                doc_id = await add_to_knowledge_base(
                    knowledge_base,
                    text_content,
                    file.filename,
                    metadata={
                        "type": "full_document",
                        "uploaded_by": current_user.email,
                        "upload_date": datetime.now().isoformat(),
                        "document_uuid": doc_uuid
                    }
                )
                
                # Save to database
                db_doc = KnowledgeDocument(
                    document_id=doc_uuid,
                    filename=file.filename,
                    file_path=str(file_path),
                    file_hash=file_hash,
                    file_size=len(content),
                    extension=file_ext,
                    text_length=len(text_content),
                    chunk_count=1,
                    is_indexed=True,
                    indexed_at=datetime.now(),
                    uploaded_by_id=current_user.id
                )
                db.add(db_doc)
                db.commit()
                
                results.append({
                    "filename": file.filename,
                    "status": "success",
                    "processing_mode": "full_content",
                    "document_id": doc_uuid,
                    "chunks": 1,
                    "characters": len(text_content),
                    "size_mb": len(content) / 1024 / 1024
                })
            else:
                # Intelligent chunking with reduced overlap for speed
                chunks = smart_chunk_text(text_content, chunk_size=chunk_size, overlap=50)
                
                chunk_ids = []
                for i, chunk in enumerate(chunks):
                    doc_id = await add_to_knowledge_base(
                        knowledge_base,
                        chunk,
                        f"{file.filename} (Part {i+1}/{len(chunks)})",
                        metadata={
                            "type": "chunk",
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "uploaded_by": current_user.email,
                            "upload_date": datetime.now().isoformat(),
                            "document_uuid": doc_uuid
                        }
                    )
                    chunk_ids.append(doc_id)
                
                # Save to database
                db_doc = KnowledgeDocument(
                    document_id=doc_uuid,
                    filename=file.filename,
                    file_path=str(file_path),
                    file_hash=file_hash,
                    file_size=len(content),
                    extension=file_ext,
                    text_length=len(text_content),
                    chunk_count=len(chunks),
                    is_indexed=True,
                    indexed_at=datetime.now(),
                    uploaded_by_id=current_user.id
                )
                db.add(db_doc)
                db.commit()
                
                results.append({
                    "filename": file.filename,
                    "status": "success",
                    "processing_mode": "intelligent_chunking",
                    "document_id": doc_uuid,
                    "document_ids": chunk_ids,
                    "chunks": len(chunks),
                    "characters": len(text_content),
                    "avg_chunk_size": len(text_content) // len(chunks) if chunks else 0,
                    "size_mb": len(content) / 1024 / 1024
                })
            
            logger.info(f"Successfully processed {file.filename}: {len(text_content)} characters")
            
        except Exception as e:
            error_msg = str(e) if str(e).strip() else f"{type(e).__name__}: PDF extraction or processing failed"
            logger.error(f"Error processing {file.filename}: {error_msg}")
            import traceback
            logger.error(traceback.format_exc())
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": error_msg if error_msg.strip() else "Unknown error during processing",
                "chunks": 0,
                "characters": 0
            })
    
    # Summary
    successful = sum(1 for r in results if r["status"] == "success")
    failed = len(results) - successful
    total_chunks = sum(r.get("chunks", 0) for r in results)
    
    return {
        "message": f"Processed {len(files)} files: {successful} successful, {failed} failed",
        "summary": {
            "total_files": len(files),
            "successful": successful,
            "failed": failed,
            "total_chunks_created": total_chunks,
            "total_size_mb": total_size / 1024 / 1024
        },
        "results": results
    }


async def extract_pdf_text(file_path: Path, use_full_content: bool = True) -> str:
    """
    Extract text from PDF using PyMuPDF (fitz).
    Supports full extraction with formatting preservation.
    """
    try:
        import fitz  # PyMuPDF
        
        logger.info(f"Opening PDF: {file_path}")
        doc = fitz.open(str(file_path))
        page_count = len(doc)
        logger.info(f"PDF opened successfully: {page_count} pages")
        
        text_parts = []
        
        for page_num, page in enumerate(doc, 1):
            # Extract text with layout preservation
            text = page.get_text("text")
            
            if use_full_content:
                # Include page headers and formatting
                text_parts.append(f"\n--- Page {page_num} ---\n")
                text_parts.append(text)
            else:
                # Clean text for chunking
                text_parts.append(text)
            
            # Log progress every 50 pages
            if page_num % 50 == 0:
                logger.info(f"Processed {page_num}/{page_count} pages...")
        
        doc.close()
        full_text = "\n".join(text_parts)
        
        logger.info(f"[OK] Extracted {len(full_text)} characters from PDF with {page_count} pages")
        return full_text
        
    except ImportError as e:
        logger.warning(f"PyMuPDF not available: {e}, using fallback")
        # Fallback to basic text extraction
        return await extract_pdf_text_fallback(file_path)
    except Exception as e:
        logger.error(f"[ERROR] PDF extraction error for {file_path}: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return ""


async def extract_pdf_text_fallback(file_path: Path) -> str:
    """Fallback PDF extraction using PyPDF2"""
    try:
        import PyPDF2
        
        text_parts = []
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        
        return "\n".join(text_parts)
    except Exception as e:
        logger.error(f"Fallback PDF extraction error: {e}")
        return ""


async def extract_word_text(file_path: Path) -> str:
    """Extract text from Word documents"""
    try:
        import docx
        
        doc = docx.Document(str(file_path))
        text_parts = []
        
        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text)
        
        # Extract tables
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells)
                if row_text.strip():
                    text_parts.append(row_text)
        
        return "\n".join(text_parts)
    except ImportError:
        logger.warning("python-docx not available")
        return ""
    except Exception as e:
        logger.error(f"Word extraction error: {e}")
        return ""


def smart_chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Intelligent text chunking that respects:
    - Paragraph boundaries
    - Sentence boundaries
    - Section headers
    """
    chunks = []
    
    # Split by paragraphs first
    paragraphs = text.split('\n\n')
    
    current_chunk = ""
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # If adding this paragraph exceeds chunk_size
        if len(current_chunk) + len(para) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk)
                # Add overlap from end of previous chunk
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_text + "\n\n" + para
            else:
                # Paragraph itself is too long, split by sentences
                sentences = para.split('. ')
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) > chunk_size:
                        if current_chunk:
                            chunks.append(current_chunk)
                            current_chunk = current_chunk[-overlap:] + ". " + sentence
                        else:
                            # Sentence too long, force split
                            chunks.append(sentence[:chunk_size])
                            current_chunk = sentence[chunk_size:]
                    else:
                        current_chunk += (". " if current_chunk else "") + sentence
        else:
            current_chunk += ("\n\n" if current_chunk else "") + para
    
    # Add remaining chunk
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks


async def add_to_knowledge_base(kb, text: str, source: str, metadata: Dict[str, Any]) -> str:
    """Add document to knowledge base with LOCAL EMBEDDING (NO API, NO COST, FAST)"""
    try:
        # Use LOCAL vector KB (sentence-transformers, no OpenAI)
        from app.services.local_vector_kb import get_local_knowledge_base
        local_kb = get_local_knowledge_base()
        
        logger.info(f"[INBOX] Adding to LOCAL vector KB: {source} ({len(text)} chars)")
        
        # Prepare metadata with document_id for linking
        full_metadata = {
            "source": source,
            **metadata
        }
        
        # Ensure document_id is available for reference links
        if 'document_uuid' in metadata:
            full_metadata['document_id'] = metadata['document_uuid']
        
        chunks_added = local_kb.add_document(
            content=text,
            metadata=full_metadata,
            chunk_size=2000,
            chunk_overlap=50
        )
        
        logger.info(f"[OK] LOCAL KB: {source} - {chunks_added} chunks (NO API COST)")
        return f"local_{chunks_added}_chunks"
        
    except Exception as e:
        logger.warning(f"Local vector KB failed, trying fallback: {e}")
        
        try:
            # Fallback to enhanced KB
            doc_id = kb.add_document(text, source, metadata)
            logger.info(f"[OK] Fallback KB: {source} (ID: {doc_id})")
            return doc_id
        except Exception as e2:
            # Last resort: generate ID
            import hashlib
            doc_id = hashlib.md5(f"{source}{text[:100]}".encode()).hexdigest()[:12]
            logger.warning(f"[WARNING] Basic storage: {source} (ID: {doc_id})")
            return doc_id


@router.get("/statistics")
async def get_statistics():
    """Get knowledge base statistics (aggregated).

    Returns a structure tailored for the frontend KnowledgeBase page:
    - total_documents: number of indexed documents in database
    - total_chunks: number of indexed chunks (aggregated from documents)
    - knowledge_level: derived from chunk count
    - search_mode: current KB mode
    - pdf_sources: known PDF files and whether they are indexed
    - categories: unique document categories
    """
    logger.info("==== STATISTICS ENDPOINT CALLED ====")
    try:
        # Local vector KB (sentence-transformers + FAISS, no API cost)
        logger.info("About to call get_local_knowledge_base()...")
        local_kb = get_local_knowledge_base()
        logger.info("Successfully got local KB instance")
        local_stats = local_kb.get_statistics()
        logger.info("Successfully got local KB statistics")

        # Query database directly for document count and chunks
        db_gen = get_db()
        db = next(db_gen)
        try:
            # Get document count and total chunks from database
            db_docs = db.query(KnowledgeDocument).all()
            db_doc_count = len(db_docs)
            db_total_chunks = sum(doc.chunk_count or 0 for doc in db_docs)
            
            # Get unique categories
            db_categories = set()
            for doc in db_docs:
                if doc.category and doc.category.strip():
                    db_categories.add(doc.category.strip())
            
            logger.info(f"Database query: {db_doc_count} documents, {db_total_chunks} chunks, {len(db_categories)} categories")
        finally:
            db.close()
        
        # Enhanced KB (medical database, optional re-ranking) - keep for capabilities
        enhanced_kb = get_knowledge_base()
        enhanced_stats = enhanced_kb.get_statistics()
        
        # Use database count as primary source
        enhanced_doc_count = db_doc_count

        # Uploads directory (files uploaded via API/UI)
        upload_files = [f for f in UPLOAD_DIR.glob("*") if f.is_file()]
        total_upload_size = sum(f.stat().st_size for f in upload_files)

        # Medical books directory (pre-seeded PDFs)
        MEDICAL_BOOKS_DIR = Path("data/medical_books")
        medical_books_files: List[Path] = []
        if MEDICAL_BOOKS_DIR.exists():
            medical_books_files = [
                f for f in MEDICAL_BOOKS_DIR.glob("**/*")
                if f.is_file() and f.suffix.lower() in {".pdf", ".txt"}
            ]

        # Determine which sources are indexed by looking at metadata 'source'
        indexed_sources = set()
        try:
            for doc_meta in getattr(local_kb, 'documents', []):
                src = str(doc_meta.get('source') or '').strip()
                if src:
                    # Normalize base filename (strip chunk labels like "(Part x/y)")
                    base = src.split(' (Part')[0].strip()
                    indexed_sources.add(base)
        except Exception:
            pass

        def _file_entry(p: Path) -> Dict[str, Any]:
            name = p.name
            status = 'indexed' if name in indexed_sources else 'available'
            return {
                'name': name,
                'size_mb': round(p.stat().st_size / 1024 / 1024, 2),
                'status': status
            }

        pdf_sources: List[Dict[str, Any]] = []
        # Include medical_books first, then uploads
        pdf_sources.extend([_file_entry(p) for p in medical_books_files[:100]])  # cap list for payload size
        pdf_sources.extend([_file_entry(p) for p in upload_files[:100]])

        # Compute knowledge level from chunks
        total_chunks = int(local_stats.get('total_chunks', 0))
        if total_chunks >= 20000:
            knowledge_level = 'expert'
        elif total_chunks >= 10000:
            knowledge_level = 'advanced'
        elif total_chunks >= 1000:
            knowledge_level = 'intermediate'
        elif total_chunks > 0:
            knowledge_level = 'basic'
        else:
            knowledge_level = 'unknown'

        # Determine search mode
        search_mode = 'local-semantic' if local_stats.get('faiss_available') else 'simple'

        return {
            'status': 'ready',
            'total_documents': db_doc_count,  # Documents from database
            'local_faiss_documents': int(local_stats.get('total_documents', 0)),  # FAISS index count
            'total_chunks': db_total_chunks,  # Chunks from database
            'categories': list(db_categories),  # List of unique categories
            'categories_count': len(db_categories),  # Count of unique categories
            'knowledge_level': knowledge_level.upper(),
            'search_mode': search_mode,
            'pdf_sources': pdf_sources,
            # Additional diagnostics
            'embedding_model': local_stats.get('embedding_model'),
            'embedding_dimension': local_stats.get('embedding_dimension'),
            'faiss_available': local_stats.get('faiss_available'),
            'model_loaded': local_stats.get('model_loaded'),
            'uploaded_files': len(upload_files),
            'total_upload_size_mb': round(total_upload_size / 1024 / 1024, 2),
            'medical_books_dir': str(MEDICAL_BOOKS_DIR.resolve()) if MEDICAL_BOOKS_DIR.exists() else None,
            'medical_books_count': len(medical_books_files),
            'capabilities': enhanced_stats.get('capabilities', {})
        }
    except Exception as e:
        # Convert exception to ASCII-safe message without using str() which may trigger rich formatting
        import traceback
        import sys
        tb_lines = traceback.format_exception(type(e), e, e.__traceback__)
        # Convert each line to ASCII
        safe_tb = []
        for line in tb_lines:
            try:
                safe_line = line.encode('ascii', errors='replace').decode('ascii')
                safe_tb.append(safe_line)
            except:
                safe_tb.append("Error in exception formatting")
        
        error_msg = "Unknown error"
        try:
            error_msg = repr(e).encode('ascii', errors='replace').decode('ascii')
        except:
            error_msg = "Error occurred"
        
        logger.error(f"Error getting statistics: {error_msg}\nTraceback:\n{''.join(safe_tb)}")
        return {'status': 'error', 'error': error_msg, 'total_documents': 0, 'total_chunks': 0, 'knowledge_level': 'UNKNOWN'}


@router.post("/search")
async def search_knowledge_base(request: SearchRequest):
    """Search knowledge base"""
    try:
        # Try local vector KB first (this is what chat uses)
        try:
            local_kb = get_local_knowledge_base()
            results = local_kb.search(request.query, top_k=request.top_k)
            
            # Filter by minimum score
            filtered_results = [
                r for r in results
                if r.get("score", 0) >= request.min_score
            ]
            
            return {
                "query": request.query,
                "results": filtered_results,
                "total_results": len(filtered_results),
                "top_k": request.top_k,
                "source": "local_vector_kb"
            }
        except Exception as local_error:
            logger.warning(f"Local KB search failed: {local_error}, trying enhanced KB")
            
            # Fallback to enhanced KB
            knowledge_base = get_knowledge_base()
            results = knowledge_base.search(request.query, top_k=request.top_k)
            
            # Filter by minimum score
            filtered_results = [
                r for r in results
                if r.get("score", 0) >= request.min_score
            ]
            
            return {
                "query": request.query,
                "results": filtered_results,
                "total_results": len(filtered_results),
                "top_k": request.top_k,
                "source": "enhanced_kb"
            }
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/documents")
async def list_documents():
    """List all uploaded documents"""
    try:
        upload_files = list(UPLOAD_DIR.glob("*"))
        documents = []
        
        for file_path in upload_files:
            if file_path.is_file():
                stat = file_path.stat()
                documents.append({
                    "filename": file_path.name,
                    "size_mb": stat.st_size / 1024 / 1024,
                    "uploaded_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # Sort by upload date (newest first)
        documents.sort(key=lambda x: x["uploaded_at"], reverse=True)
        
        return {
            "documents": documents,
            "total_count": len(documents),
            "total_size_mb": sum(d["size_mb"] for d in documents)
        }
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        return {"error": str(e), "documents": []}


@router.delete("/documents/{filename}")
async def delete_document(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Delete an uploaded document"""
    try:
        file_path = UPLOAD_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Document not found")
        
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="Invalid file")
        
        file_path.unlink()
        
        return {
            "message": f"Document {filename} deleted successfully",
            "filename": filename
        }
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-large")
async def upload_large_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and process large PDF files (up to 1GB).
    Uses streaming and chunking for memory efficiency.
    Ideal for medical textbooks like Oxford Handbook, Harrison's, etc.
    """
    try:
        # Validate file type
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Save file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename
        
        # Save uploaded file
        logger.info(f"Saving large file: {file.filename}")
        with open(file_path, "wb") as f:
            # Read and write in chunks to handle large files
            chunk_size = 1024 * 1024  # 1MB chunks
            while chunk := await file.read(chunk_size):
                f.write(chunk)
        
        file_size_mb = file_path.stat().st_size / 1024 / 1024
        logger.info(f"Saved {file.filename}: {file_size_mb:.2f} MB")
        
        # Validate file size
        if file_path.stat().st_size > MAX_FILE_SIZE:
            file_path.unlink()  # Delete oversized file
            raise HTTPException(
                status_code=400,
                detail=f"File exceeds maximum size of {MAX_FILE_SIZE / 1024 / 1024:.0f}MB"
            )
        
        # Process with large PDF processor
        processor = get_large_pdf_processor()
        knowledge_base = get_knowledge_base()
        
        # Progress tracking
        processing_status = {
            'current_page': 0,
            'total_pages': 0,
            'progress': 0
        }
        
        async def progress_callback(progress: float, message: str):
            processing_status['progress'] = progress
            logger.info(f"Processing: {progress:.1f}% - {message}")
        
        # Process PDF and add to KB
        result = await processor.process_large_pdf(
            file_path=file_path,
            add_to_kb=lambda text, source, metadata: add_to_knowledge_base(
                knowledge_base, text, source, metadata
            ),
            progress_callback=progress_callback
        )
        
        return {
            "message": f"Successfully processed {file.filename}",
            "filename": file.filename,
            "saved_as": safe_filename,
            "file_size_mb": file_size_mb,
            "processing_result": result,
            "uploaded_by": current_user.email,
            "upload_time": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing large PDF: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@router.get("/processor-stats")
async def get_processor_statistics():
    """Get large PDF processor statistics"""
    try:
        processor = get_large_pdf_processor()
        stats = processor.get_statistics()
        
        return {
            "processor_info": stats,
            "cache_dir": str(processor.cache_dir),
            "status": "operational"
        }
    except Exception as e:
        logger.error(f"Error getting processor stats: {e}")
        return {"error": str(e)}


@router.post("/clear-processor-cache")
async def clear_processor_cache(
    older_than_days: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    """Clear PDF extraction cache"""
    try:
        processor = get_large_pdf_processor()
        result = await processor.clear_cache(older_than_days)
        
        return {
            "message": "Cache cleared successfully",
            **result
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/clear-all")
async def clear_all_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all documents from knowledge base and database (admin only)"""
    if current_user.role != "admin" and current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only admins and doctors can clear knowledge base")
    
    try:
        # Delete all KB documents from database
        deleted_count = db.query(KnowledgeDocument).delete()
        db.commit()
        
        # Clear vector store
        knowledge_base = get_knowledge_base()
        if hasattr(knowledge_base, 'clear_all'):
            knowledge_base.clear_all()
        
        logger.info(f"Cleared {deleted_count} documents from knowledge base")
        
        return {
            "message": "Knowledge base cleared successfully",
            "documents_deleted": deleted_count
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error clearing knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/error-report")
async def get_error_report(current_user: User = Depends(get_current_user)):
    """Get automatic error correction system report"""
    corrector = get_error_corrector()
    return corrector.get_error_report()


@router.get("/documents/list")
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all uploaded documents with metadata"""
    documents = db.query(KnowledgeDocument).offset(skip).limit(limit).all()
    
    return {
        "total": db.query(KnowledgeDocument).count(),
        "documents": [
            {
                "id": doc.document_id,
                "filename": doc.filename,
                "size_mb": round(doc.file_size / 1024 / 1024, 2),
                "chunks": doc.chunk_count,
                "text_length": doc.text_length,
                "uploaded_at": doc.uploaded_at.isoformat(),
                "uploaded_by": doc.uploaded_by.email if doc.uploaded_by else None,
                "is_indexed": doc.is_indexed
            }
            for doc in documents
        ]
    }


@router.get("/documents/{document_id}")
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get document details and content by ID or filename"""
    # Try to find by UUID first
    doc = db.query(KnowledgeDocument).filter(
        KnowledgeDocument.document_id == document_id
    ).first()
    
    # If not found, try by filename
    if not doc:
        doc = db.query(KnowledgeDocument).filter(
            KnowledgeDocument.filename == document_id
        ).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get chunks for this document
    chunks = db.query(KnowledgeChunk).filter(
        KnowledgeChunk.document_id == doc.document_id
    ).order_by(KnowledgeChunk.chunk_index).all()
    
    return {
        "id": doc.document_id,
        "filename": doc.filename,
        "file_path": doc.file_path,
        "file_size": doc.file_size,
        "size_mb": round(doc.file_size / 1024 / 1024, 2),
        "text_length": doc.text_length,
        "chunk_count": doc.chunk_count,
        "uploaded_at": doc.uploaded_at.isoformat(),
        "uploaded_by": doc.uploaded_by.email if doc.uploaded_by else None,
        "is_indexed": doc.is_indexed,
        "chunks": [
            {
                "chunk_id": chunk.chunk_id,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text_content,
                "text_length": len(chunk.text_content),
                "metadata": chunk.metadata
            }
            for chunk in chunks[:10]  # Limit to first 10 chunks for performance
        ],
        "total_chunks": len(chunks)
    }


# ============================================================================
# ONLINE KNOWLEDGE BASE ENDPOINTS
# ============================================================================

_online_kb_service = None

def get_online_kb_service() -> OnlineKnowledgeService:
    """Get singleton instance of online KB service"""
    global _online_kb_service
    if _online_kb_service is None:
        _online_kb_service = OnlineKnowledgeService()
    return _online_kb_service


@router.get("/online/search-pubmed")
async def search_pubmed_online(
    query: str,
    max_results: int = 5,
    use_cache: bool = True,
    current_user: User = Depends(get_current_user)
):
    """
    Search PubMed for recent medical research (FREE - No API key required)
    
    - **query**: Search terms (e.g., "diabetes treatment", "COVID-19 symptoms")
    - **max_results**: Number of results (1-20)
    - **use_cache**: Use cached results if available (24h cache)
    
    Returns recent research articles from PubMed database
    """
    if max_results < 1 or max_results > 20:
        raise HTTPException(status_code=400, detail="max_results must be between 1 and 20")
    
    try:
        service = get_online_kb_service()
        await service.initialize()
        
        results = await service.search_pubmed(query, max_results, use_cache)
        
        return {
            "query": query,
            "total_results": len(results),
            "cached": use_cache,
            "results": results
        }
    except Exception as e:
        logger.error(f"Error searching PubMed: {e}")
        raise HTTPException(status_code=500, detail=f"PubMed search failed: {str(e)}")


@router.get("/online/guidelines")
async def get_clinical_guidelines(
    condition: str,
    use_cache: bool = True,
    current_user: User = Depends(get_current_user)
):
    """
    Get clinical practice guidelines from multiple authoritative sources
    
    - **condition**: Medical condition (e.g., "hypertension", "diabetes", "asthma")
    - **use_cache**: Use cached results (7-day cache for guidelines)
    
    Sources: PubMed, CDC, WHO, NICE (UK)
    """
    try:
        service = get_online_kb_service()
        await service.initialize()
        
        guidelines = await service.get_clinical_guidelines(condition, use_cache)
        
        # Group by source
        by_source = {}
        for guideline in guidelines:
            source = guideline.get('source', 'Unknown')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(guideline)
        
        return {
            "condition": condition,
            "total_guidelines": len(guidelines),
            "sources": list(by_source.keys()),
            "cached": use_cache,
            "by_source": by_source,
            "all_guidelines": guidelines
        }
    except Exception as e:
        logger.error(f"Error fetching guidelines: {e}")
        raise HTTPException(status_code=500, detail=f"Guidelines fetch failed: {str(e)}")


@router.get("/online/drug-info")
async def get_drug_information(
    drug_name: str,
    use_cache: bool = True,
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive drug information from online sources
    
    - **drug_name**: Drug name (generic or brand)
    - **use_cache**: Use cached results (24h cache)
    
    Returns: Indications, dosage, side effects, interactions, etc.
    """
    try:
        service = get_online_kb_service()
        await service.initialize()
        
        drug_info = await service.get_drug_information(drug_name, use_cache)
        
        return {
            "drug_name": drug_name,
            "cached": use_cache,
            "information": drug_info
        }
    except Exception as e:
        logger.error(f"Error fetching drug info: {e}")
        raise HTTPException(status_code=500, detail=f"Drug info fetch failed: {str(e)}")


@router.get("/online/status")
async def online_kb_status(current_user: User = Depends(get_current_user)):
    """
    Get status of online knowledge base service
    
    Returns cache statistics and service availability
    """
    try:
        service = get_online_kb_service()
        await service.initialize()
        
        # Get cache stats
        cache_dir = service.cache_dir
        cache_files = list(cache_dir.glob("*.json"))
        total_cache_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            "status": "operational",
            "initialized": service.initialized,
            "cache_directory": str(cache_dir),
            "cache_files": len(cache_files),
            "cache_size_mb": round(total_cache_size / 1024 / 1024, 2),
            "cache_duration_hours": service.cache_duration.total_seconds() / 3600,
            "features": {
                "pubmed_search": "Available (FREE)",
                "clinical_guidelines": "Available (PubMed, CDC, WHO, NICE)",
                "drug_information": "Available",
                "medical_news": "Available"
            }
        }
    except Exception as e:
        logger.error(f"Error getting online KB status: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.delete("/online/clear-cache")
async def clear_online_cache(current_user: User = Depends(get_current_user)):
    """
    Clear online knowledge base cache
    
    Forces fresh data fetching on next request
    """
    if current_user.role not in ["admin", "doctor"]:
        raise HTTPException(status_code=403, detail="Only admins and doctors can clear cache")
    
    try:
        service = get_online_kb_service()
        await service.initialize()
        
        cache_dir = service.cache_dir
        cache_files = list(cache_dir.glob("*.json"))
        deleted_count = 0
        
        for cache_file in cache_files:
            cache_file.unlink()
            deleted_count += 1
        
        return {
            "message": "Online KB cache cleared",
            "files_deleted": deleted_count
        }
    except Exception as e:
        logger.error(f"Error clearing online cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/enhanced")
async def enhanced_search(
    request: SearchRequest,
    include_images: bool = True,
    verify_online: bool = True,
    current_user: User = Depends(get_current_user)
):
    """
    Enhanced KB search with images and online verification
    
    - **query**: Search query
    - **top_k**: Number of results (default 5)
    - **include_images**: Include related medical images from PDFs
    - **verify_online**: Verify content against current medical guidelines
    
    Returns: Text results + images + verification status
    """
    try:
        from app.services.enhanced_kb_processor import EnhancedKBProcessor, enhance_kb_search
        
        # Get KB services
        kb_service = get_local_knowledge_base()
        processor = EnhancedKBProcessor()
        
        # Perform enhanced search
        results = processor.search_with_images(
            query=request.query,
            kb_service=kb_service,
            include_images=include_images,
            top_k=request.top_k
        )
        
        # Add metadata
        results['query'] = request.query
        results['include_images'] = include_images
        results['verify_online'] = verify_online
        results['timestamp'] = datetime.now().isoformat()
        
        return results
        
    except Exception as e:
        logger.error(f"Enhanced search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/images/{document_id}")
async def get_document_images(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get all images extracted from a specific document
    
    Returns list of images with captions and descriptions
    """
    try:
        from app.services.enhanced_kb_processor import EnhancedKBProcessor
        
        processor = EnhancedKBProcessor()
        images = processor._get_images_for_document(document_id)
        
        # Generate AI descriptions for each image
        for img in images:
            if 'description' not in img:
                img['description'] = processor.generate_image_description(img['path'])
        
        return {
            "document_id": document_id,
            "total_images": len(images),
            "images": images
        }
        
    except Exception as e:
        logger.error(f"Error getting document images: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-images/{document_id}")
async def extract_document_images(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Extract and save images from a specific PDF document
    
    This is a background task that can take time for large PDFs
    """
    if current_user.role not in ["admin", "doctor"]:
        raise HTTPException(status_code=403, detail="Only admins and doctors can extract images")
    
    try:
        from app.services.enhanced_kb_processor import EnhancedKBProcessor
        
        # Find document in database
        doc = db.query(KnowledgeDocument).filter(
            KnowledgeDocument.document_id == document_id
        ).first()
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if not doc.file_path or not Path(doc.file_path).exists():
            raise HTTPException(status_code=404, detail="PDF file not found on disk")
        
        # Extract images
        processor = EnhancedKBProcessor()
        extraction_result = processor.extract_text_and_images(doc.file_path)
        
        if 'error' in extraction_result:
            raise HTTPException(status_code=500, detail=extraction_result['error'])
        
        # Save images
        saved_images = []
        for img in extraction_result['images']:
            img_path = processor.save_image(
                image_data=img['image_data'],
                image_hash=f"{document_id}_{img['hash']}",
                format=img['format']
            )
            saved_images.append({
                'path': img_path,
                'page': img['page'],
                'caption': img['caption'],
                'size_kb': img['size'] / 1024
            })
        
        return {
            "document_id": document_id,
            "filename": doc.filename,
            "extraction_complete": True,
            "total_images": len(saved_images),
            "images": saved_images,
            "metadata": extraction_result['metadata']
        }
        
    except Exception as e:
        logger.error(f"Error extracting images: {e}")
        raise HTTPException(status_code=500, detail=str(e))
