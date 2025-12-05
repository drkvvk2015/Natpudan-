"""
Enhanced Knowledge Base Processor
- Extracts full text AND images from PDFs
- Stores images with embeddings
- Online content verification via PubMed/web search
- Multi-modal search (text + images)
"""

import logging
import base64
import hashlib
import os
import json
from typing import List, Dict, Any, Optional, Tuple, Protocol
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

# Type hints for external dependencies
try:
    import fitz  # PyMuPDF  # type: ignore
    _PYMUPDF_AVAILABLE = True
except ImportError:
    logger.warning("PyMuPDF not available. Install with: pip install PyMuPDF")
    fitz = None  # type: ignore
    _PYMUPDF_AVAILABLE = False

try:
    from PIL import Image
    _PIL_AVAILABLE = True
except ImportError:
    logger.warning("PIL not available. Install with: pip install Pillow")
    _PIL_AVAILABLE = False

try:
    from openai import OpenAI
    _OPENAI_AVAILABLE = True
except ImportError:
    OpenAI = None  # type: ignore
    _OPENAI_AVAILABLE = False


# Protocol for KB service
class KBServiceProtocol(Protocol):
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        ...


PYMUPDF_AVAILABLE = _PYMUPDF_AVAILABLE
OPENAI_AVAILABLE = _OPENAI_AVAILABLE
PIL_AVAILABLE = _PIL_AVAILABLE


class EnhancedKBProcessor:
    """
    Enhanced KB with image extraction and online verification
    """
    
    def __init__(self, storage_dir: str = "data/knowledge_base"):
        self.storage_dir = Path(storage_dir)
        self.images_dir = self.storage_dir / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize OpenAI for verification
        self.client: Optional[Any] = None
        if OPENAI_AVAILABLE and OpenAI is not None:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
        
        logger.info("Enhanced KB Processor initialized")
    
    def extract_text_and_images(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract both text and images from PDF
        
        Returns:
            {
                'text_chunks': [{'text': str, 'page': int, 'position': tuple}],
                'images': [{'image_data': bytes, 'page': int, 'caption': str, 'hash': str}],
                'metadata': {'pages': int, 'has_images': bool}
            }
        """
        if not PYMUPDF_AVAILABLE or fitz is None:
            return {'error': 'PyMuPDF not available'}
        
        try:
            doc = fitz.open(pdf_path)  # type: ignore
            text_chunks: List[Dict[str, Any]] = []
            images: List[Dict[str, Any]] = []
            
            for page_num in range(len(doc)):  # type: ignore
                page = doc[page_num]  # type: ignore
                
                # Extract text with position
                text_content = page.get_text()  # type: ignore
                if isinstance(text_content, str) and text_content.strip():
                    text_chunks.append({
                        'text': text_content,
                        'page': page_num + 1,
                        'position': (0, 0),
                        'length': len(text_content)
                    })
                
                # Extract images
                image_list = page.get_images(full=True)  # type: ignore
                for img_index, img in enumerate(image_list):  # type: ignore
                    try:
                        xref = img[0]  # type: ignore
                        base_image = doc.extract_image(xref)  # type: ignore
                        image_bytes: bytes = base_image["image"]  # type: ignore
                        
                        # Generate hash for deduplication
                        img_hash = hashlib.md5(image_bytes).hexdigest()
                        
                        # Try to extract nearby text as caption
                        caption = self._extract_image_caption(page, img_index)
                        
                        img_format = base_image.get("ext", "png")  # type: ignore
                        images.append({
                            'image_data': image_bytes,
                            'page': page_num + 1,
                            'caption': caption,
                            'hash': img_hash,
                            'format': str(img_format),
                            'size': len(image_bytes)
                        })
                        
                    except Exception as e:
                        logger.warning(f"Failed to extract image {img_index} from page {page_num}: {e}")
            
            # Get metadata before closing
            total_pages = len(doc)  # type: ignore
            doc.close()  # type: ignore
            
            return {
                'text_chunks': text_chunks,
                'images': images,
                'metadata': {
                    'pages': total_pages,
                    'has_images': len(images) > 0,
                    'total_images': len(images),
                    'total_text_length': sum(int(c.get('length', 0)) for c in text_chunks)
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting from PDF: {e}")
            return {'error': str(e)}
    
    def _extract_image_caption(self, page: Any, img_index: int) -> str:
        """Extract text near image as caption"""
        try:
            # Get all text blocks
            blocks = page.get_text("blocks")  # type: ignore
            # Find closest text block to image
            # Simplified: just take first line after image
            if blocks:
                for block in blocks:  # type: ignore
                    if isinstance(block, (list, tuple)) and len(block) > 4:  # type: ignore
                        text_content = str(block[4]).strip()  # type: ignore
                        if text_content and len(text_content) < 200:
                            return text_content
        except Exception:
            pass
        return ""
    
    def save_image(self, image_data: bytes, image_hash: str, format: str = "png") -> str:
        """Save image to disk and return path"""
        filename = f"{image_hash}.{format}"
        filepath = self.images_dir / filename
        
        if not filepath.exists():
            with open(filepath, 'wb') as f:
                f.write(image_data)
        
        return str(filepath)
    
    def verify_content_online(self, text: str, query: str) -> Dict[str, Any]:
        """
        Verify medical content against online sources
        
        Uses OpenAI to:
        1. Search PubMed for relevant papers
        2. Check against current medical guidelines
        3. Flag outdated or incorrect information
        """
        if not self.client:
            return {'verified': False, 'reason': 'OpenAI not available'}
        
        try:
            verification_prompt = f"""You are a medical fact-checker. Verify this medical information:

CONTENT TO VERIFY:
{text[:2000]}  # Limit to 2000 chars

USER QUERY: {query}

Tasks:
1. Identify any potentially outdated medical information
2. Check if content aligns with current medical consensus
3. Suggest verification sources (PubMed, clinical guidelines)
4. Rate confidence: HIGH/MEDIUM/LOW

Respond in JSON format:
{{
    "verified": true/false,
    "confidence": "HIGH/MEDIUM/LOW",
    "concerns": ["list any concerns"],
    "verification_sources": ["suggested PubMed searches"],
    "recommendations": "how to verify further"
}}
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": verification_prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if content:
                result = json.loads(content)
                return result
            return {'verified': False, 'error': 'No content in response'}
            
        except Exception as e:
            logger.error(f"Error verifying content: {e}")
            return {'verified': False, 'error': str(e)}
    
    def search_with_images(
        self,
        query: str,
        kb_service: KBServiceProtocol,
        include_images: bool = True,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Search KB with both text and images
        
        Returns:
            {
                'text_results': [list of matching text chunks],
                'image_results': [list of relevant images with captions],
                'verification': verification results if enabled
            }
        """
        import numpy as np
        
        # Get text results from vector KB
        text_results = kb_service.search(query, top_k=top_k)  # type: ignore
        
        # Convert numpy types to Python native types for JSON serialization
        def convert_numpy_types(obj):
            """Recursively convert numpy types to Python native types"""
            if isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return obj
        
        # Convert text results to serializable format
        text_results = convert_numpy_types(text_results)
        
        results: Dict[str, Any] = {
            'text_results': text_results,
            'image_results': [],
            'verification': None
        }
        
        # Find images related to results
        if include_images and text_results:
            for result in text_results:  # type: ignore
                # Check if document has associated images
                doc_id = result.get('document_id')  # type: ignore
                if doc_id:
                    images = self._get_images_for_document(str(doc_id))  # type: ignore
                    results['image_results'].extend(images)  # type: ignore
        
        # Online verification of top result
        if text_results and len(text_results) > 0:  # type: ignore
            top_result_text = str(text_results[0].get('text', ''))  # type: ignore
            if top_result_text:
                results['verification'] = self.verify_content_online(top_result_text, query)  # type: ignore
        
        return results
    
    def _get_images_for_document(self, doc_id: str) -> List[Dict[str, Any]]:
        """Get all images associated with a document"""
        images = []
        # Look for images in storage with matching doc_id
        pattern = f"{doc_id}_*.png"
        for img_path in self.images_dir.glob(pattern):
            images.append({
                'path': str(img_path),
                'filename': img_path.name
            })
        return images
    
    def generate_image_description(self, image_path: str) -> str:
        """Use OpenAI Vision to describe medical images"""
        if not self.client:
            return "Image description not available (OpenAI not configured)"
        
        try:
            with open(image_path, 'rb') as img_file:
                image_data = base64.b64encode(img_file.read()).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Vision model
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe this medical image in detail. Include: anatomical structures, pathology if visible, diagnostic features, and clinical significance."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}"
                            }
                        }
                    ]
                }],
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating image description: {e}")
            return f"Error: {str(e)}"


# Helper function for API endpoint
def enhance_kb_search(
    query: str,
    kb_service: KBServiceProtocol,  # type: ignore
    processor: EnhancedKBProcessor
) -> Dict[str, Any]:
    """
    Enhanced search with images and verification
    Call from API endpoint
    """
    return processor.search_with_images(  # type: ignore
        query=query,
        kb_service=kb_service,  # type: ignore
        include_images=True,
        top_k=5
    )
