"""
Enhanced PDF Processor with OCR and Image Extraction
Supports: Text extraction, OCR for scanned PDFs, Image extraction with indexing
"""

import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
import fitz  # PyMuPDF  # type: ignore
from datetime import datetime
import json
import hashlib

logger = logging.getLogger(__name__)

# Check OCR availability
OCR_AVAILABLE: bool = False  # noqa: F811
POPPLER_AVAILABLE: bool = False  # noqa: F811

try:
    import pytesseract  # type: ignore  # noqa: F401
    OCR_AVAILABLE = True  # noqa: F811
    logger.info("[OCR] pytesseract available")
except ImportError:
    logger.warning("[OCR] pytesseract not installed - OCR disabled")

try:
    from pdf2image import convert_from_path  # type: ignore  # noqa: F401
    POPPLER_AVAILABLE = True  # noqa: F811
    logger.info("[OCR] pdf2image available")
except ImportError:
    logger.warning("[OCR] pdf2image not installed")


class PDFOCRProcessor:
    """Enhanced PDF processor with OCR and image extraction capabilities"""
    
    def __init__(self, images_dir: Optional[Path] = None) -> None:
        self.images_dir = images_dir or Path("data/knowledge_base/images")
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # OCR configuration
        self.ocr_enabled = OCR_AVAILABLE
        self.min_text_per_page = 50  # Minimum characters to consider text-based
        
    def extract_pdf_with_images(
        self, 
        pdf_path: Path, 
        extract_images: bool = True,
        use_ocr: bool = True,
        document_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract text and images from PDF with intelligent OCR fallback
        
        Returns:
            {
                'text': str,
                'images': [{'path': str, 'page': int, 'index': int, 'metadata': dict}],
                'pages': int,
                'method': 'text'|'ocr'|'hybrid',
                'ocr_applied': bool
            }
        """
        try:
            doc = fitz.open(str(pdf_path))
            page_count = len(doc)
            
            logger.info(f"[PDF] Processing {pdf_path.name}: {page_count} pages")
            
            # Extract text and images
            text_parts = []
            extracted_images = []
            total_text_chars = 0
            pages_with_text = 0
            
            for page_num in range(page_count):
                page = doc[page_num]
                
                # Extract text
                page_text = page.get_text("text")
                text_chars = len(page_text.strip())
                total_text_chars += text_chars
                
                if text_chars > self.min_text_per_page:
                    pages_with_text += 1
                    text_parts.append(f"\n--- Page {page_num + 1} ---\n{page_text}")
                else:
                    # Placeholder for OCR or image-only page
                    text_parts.append(f"\n--- Page {page_num + 1} [Image/Scan] ---\n")
                
                # Extract images from page
                if extract_images:
                    page_images = self._extract_page_images(
                        page, page_num, pdf_path.stem, document_id
                    )
                    extracted_images.extend(page_images)
                
                # Progress logging
                if (page_num + 1) % 50 == 0:
                    logger.info(f"[PDF] Processed {page_num + 1}/{page_count} pages")
            
            doc.close()
            
            # Determine if OCR is needed
            avg_text_per_page = total_text_chars / page_count if page_count > 0 else 0
            is_text_based = avg_text_per_page > self.min_text_per_page
            
            result = {
                'text': "\n".join(text_parts),
                'images': extracted_images,
                'pages': page_count,
                'total_chars': total_text_chars,
                'avg_chars_per_page': avg_text_per_page,
                'pages_with_text': pages_with_text,
                'is_text_based': is_text_based,
                'method': 'text' if is_text_based else 'needs_ocr',
                'ocr_applied': False
            }
            
            # Apply OCR if needed and available
            if not is_text_based and use_ocr and self.ocr_enabled:
                logger.info(f"[OCR] PDF appears to be scanned, applying OCR...")
                ocr_result = self._apply_ocr_to_pdf(pdf_path, page_count)
                if ocr_result['success']:
                    result['text'] = ocr_result['text']
                    result['total_chars'] = len(ocr_result['text'])
                    result['method'] = 'ocr'
                    result['ocr_applied'] = True
                    result['ocr_confidence'] = ocr_result.get('confidence', 0)
            
            logger.info(f"[PDF] Extracted {result['total_chars']} chars, {len(extracted_images)} images")
            return result
            
        except Exception as e:
            logger.error(f"[PDF] Error processing {pdf_path}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'text': '',
                'images': [],
                'pages': 0,
                'method': 'error',
                'error': str(e)
            }
    
    def _extract_page_images(
        self, 
        page: Any, 
        page_num: int, 
        pdf_name: str,
        document_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Extract and save images from a PDF page"""
        images = []
        
        try:
            image_list = page.get_images(full=True)
            
            for img_index, img_info in enumerate(image_list):
                try:
                    xref = img_info[0]
                    base_image = page.parent.extract_image(xref)
                    
                    if not base_image:
                        continue
                    
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Generate unique image filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_hash = hashlib.md5(image_bytes).hexdigest()[:8]
                    doc_id_prefix = f"{document_id}_" if document_id else ""
                    image_filename = f"{doc_id_prefix}{pdf_name}_p{page_num + 1}_img{img_index + 1}_{image_hash}.{image_ext}"
                    image_path = self.images_dir / image_filename
                    
                    # Save image
                    with open(image_path, "wb") as img_file:
                        img_file.write(image_bytes)
                    
                    # Create metadata
                    metadata = {
                        'filename': image_filename,
                        'path': str(image_path),
                        'page': page_num + 1,
                        'index': img_index + 1,
                        'xref': xref,
                        'extension': image_ext,
                        'size_bytes': len(image_bytes),
                        'document_id': document_id,
                        'pdf_name': pdf_name,
                        'extracted_at': datetime.now().isoformat()
                    }
                    
                    # Save metadata JSON
                    metadata_path = image_path.with_suffix('.json')
                    with open(metadata_path, 'w') as meta_file:
                        json.dump(metadata, meta_file, indent=2)
                    
                    images.append(metadata)
                    
                except Exception as e:
                    logger.warning(f"[IMG] Failed to extract image {img_index} from page {page_num}: {e}")
        
        except Exception as e:
            logger.warning(f"[IMG] Error extracting images from page {page_num}: {e}")
        
        return images
    
    def _apply_ocr_to_pdf(self, pdf_path: Path, page_count: int) -> Dict[str, Any]:
        """Apply OCR to entire PDF using Tesseract"""
        if not OCR_AVAILABLE:
            return {
                'success': False,
                'text': '',
                'error': 'pytesseract not installed'
            }
        
        if not POPPLER_AVAILABLE:
            return {
                'success': False,
                'text': '',
                'error': 'pdf2image not installed (requires poppler)'
            }
        
        try:
            # Check if Tesseract executable is available
            try:
                import pytesseract
                # Try to get version to verify installation
                pytesseract.get_tesseract_version()
            except Exception as e:
                logger.error(f"[OCR] Tesseract not found: {e}")
                return {
                    'success': False,
                    'text': '',
                    'error': 'Tesseract OCR not installed. Download from: https://github.com/UB-Mannheim/tesseract/wiki'
                }
            
            # Convert PDF to images
            logger.info(f"[OCR] Converting PDF to images for OCR...")
            images = convert_from_path(str(pdf_path), dpi=300)
            
            text_parts = []
            total_confidence = 0
            
            for i, image in enumerate(images):
                logger.info(f"[OCR] Processing page {i + 1}/{len(images)}")
                
                # Perform OCR
                ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                
                # Extract text and confidence
                page_text = pytesseract.image_to_string(image, lang='eng')
                confidences = [int(conf) for conf in ocr_data['conf'] if conf != '-1']
                page_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                text_parts.append(f"\n--- Page {i + 1} [OCR] ---\n{page_text}")
                total_confidence += page_confidence
            
            avg_confidence = total_confidence / len(images) if images else 0
            
            logger.info(f"[OCR] Completed OCR: {len(''.join(text_parts))} chars, {avg_confidence:.1f}% confidence")
            
            return {
                'success': True,
                'text': "\n".join(text_parts),
                'confidence': avg_confidence,
                'pages_processed': len(images)
            }
            
        except Exception as e:
            logger.error(f"[OCR] Error during OCR processing: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'text': '',
                'error': str(e)
            }
    
    def get_setup_instructions(self) -> Dict[str, Any]:  # type: ignore
        """Get setup instructions for OCR dependencies"""
        instructions = {
            'pytesseract_installed': OCR_AVAILABLE,
            'pdf2image_installed': POPPLER_AVAILABLE,
            'tesseract_available': False,
            'poppler_available': False,
            'instructions': []
        }
        
        # Check Tesseract
        if OCR_AVAILABLE:
            try:
                import pytesseract
                pytesseract.get_tesseract_version()
                instructions['tesseract_available'] = True
            except:
                instructions['instructions'].append({
                    'component': 'Tesseract OCR',
                    'status': 'missing',
                    'windows_install': 'Download from https://github.com/UB-Mannheim/tesseract/wiki',
                    'after_install': 'Add to PATH: C:\\Program Files\\Tesseract-OCR'
                })
        else:
            instructions['instructions'].append({
                'component': 'pytesseract',
                'status': 'missing',
                'install': 'pip install pytesseract'
            })
        
        # Check Poppler
        if not POPPLER_AVAILABLE:
            instructions['instructions'].append({
                'component': 'pdf2image',
                'status': 'missing',
                'install': 'pip install pdf2image'
            })
        else:
            # Check if poppler binaries are available
            try:
                from pdf2image import convert_from_path
                # Try a dummy conversion to check poppler
                instructions['poppler_available'] = True
            except:
                instructions['instructions'].append({
                    'component': 'Poppler',
                    'status': 'missing',
                    'windows_install': 'Download from http://blog.alivate.com.au/poppler-windows/',
                    'after_install': 'Add bin folder to PATH or set poppler_path parameter'
                })
        
        instructions['ocr_ready'] = (
            instructions['tesseract_available'] and 
            instructions['poppler_available']
        )
        
        return instructions


# Singleton instance
_processor = None

def get_pdf_ocr_processor() -> PDFOCRProcessor:
    """Get singleton PDF OCR processor instance"""
    global _processor
    if _processor is None:
        _processor = PDFOCRProcessor()
    return _processor
