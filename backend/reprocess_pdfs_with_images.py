"""
Reprocess all PDFs with Enhanced KB Processor
- Extracts full text + images from all PDFs
- Generates AI descriptions for images
- Stores images with metadata
- Updates FAISS index with image references
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.enhanced_kb_processor import EnhancedKBProcessor, PYMUPDF_AVAILABLE, OPENAI_AVAILABLE

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def reprocess_all_pdfs():
    """Reprocess all PDFs with enhanced image extraction"""
    
    # Check dependencies
    if not PYMUPDF_AVAILABLE:
        logger.error("PyMuPDF not available. Install with: pip install PyMuPDF")
        return
    
    if not OPENAI_AVAILABLE:
        logger.warning("OpenAI not available - image descriptions will be skipped")
    
    # Initialize processors
    kb_path = Path("data/knowledge_base")
    processor = EnhancedKBProcessor(storage_dir=str(kb_path))
    
    # Find all PDFs
    pdf_files = list(kb_path.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    if not pdf_files:
        logger.warning("No PDF files found in knowledge base directory")
        return
    
    # Process each PDF
    stats = {
        'total_pdfs': len(pdf_files),
        'processed': 0,
        'failed': 0,
        'total_images': 0,
        'total_text_chunks': 0
    }
    
    start_time = datetime.now()
    
    for idx, pdf_path in enumerate(pdf_files, 1):
        try:
            logger.info(f"\n[{idx}/{len(pdf_files)}] Processing: {pdf_path.name}")
            
            # Extract full content with images
            result = processor.extract_text_and_images(str(pdf_path))
            
            if 'error' in result:
                logger.error(f"Error processing {pdf_path.name}: {result['error']}")
                stats['failed'] += 1
                continue
            
            # Get metadata
            metadata = result.get('metadata', {})
            text_chunks = result.get('text_chunks', [])
            images = result.get('images', [])
            
            logger.info(f"  Pages: {metadata.get('pages', 0)}")
            logger.info(f"  Text chunks: {len(text_chunks)}")
            logger.info(f"  Images found: {len(images)}")
            
            # Store images and generate AI descriptions
            stored_images = 0
            if images and OPENAI_AVAILABLE:
                doc_id = pdf_path.stem
                doc_images_dir = processor.images_dir / doc_id
                doc_images_dir.mkdir(parents=True, exist_ok=True)
                
                for img_idx, img_data in enumerate(images):
                    try:
                        img_hash = img_data['hash']
                        img_path = doc_images_dir / f"{img_hash}.{img_data['format']}"
                        
                        # Save image
                        with open(img_path, 'wb') as f:
                            f.write(img_data['image_data'])
                        
                        # Generate AI description
                        if processor.client:
                            logger.info(f"    Generating AI description for image {img_idx + 1}/{len(images)}...")
                            description = processor.generate_image_description(str(img_path))
                            
                            # Save metadata
                            metadata_path = doc_images_dir / f"{img_hash}.json"
                            import json
                            with open(metadata_path, 'w') as f:
                                json.dump({
                                    'page': img_data['page'],
                                    'caption': img_data['caption'],
                                    'description': description,
                                    'hash': img_hash,
                                    'format': img_data['format'],
                                    'size': img_data['size']
                                }, f, indent=2)
                            
                            stored_images += 1
                        
                    except Exception as e:
                        logger.warning(f"    Failed to store image {img_idx}: {e}")
                
                logger.info(f"  Stored {stored_images}/{len(images)} images with AI descriptions")
            
            # Update statistics
            stats['processed'] += 1
            stats['total_images'] += len(images)
            stats['total_text_chunks'] += len(text_chunks)
            
            # Progress report every 10 files
            if idx % 10 == 0:
                elapsed = (datetime.now() - start_time).total_seconds()
                avg_time = elapsed / idx
                remaining = (len(pdf_files) - idx) * avg_time
                logger.info(f"\n>>> Progress: {idx}/{len(pdf_files)} PDFs")
                logger.info(f">>> Estimated time remaining: {remaining/60:.1f} minutes")
            
        except Exception as e:
            logger.error(f"Failed to process {pdf_path.name}: {e}")
            stats['failed'] += 1
    
    # Final statistics
    elapsed_time = (datetime.now() - start_time).total_seconds()
    logger.info("\n" + "="*60)
    logger.info("REPROCESSING COMPLETE")
    logger.info("="*60)
    logger.info(f"Total PDFs: {stats['total_pdfs']}")
    logger.info(f"Successfully processed: {stats['processed']}")
    logger.info(f"Failed: {stats['failed']}")
    logger.info(f"Total text chunks extracted: {stats['total_text_chunks']}")
    logger.info(f"Total images extracted: {stats['total_images']}")
    logger.info(f"Time elapsed: {elapsed_time/60:.1f} minutes")
    logger.info(f"Average time per PDF: {elapsed_time/len(pdf_files):.1f} seconds")
    logger.info("="*60)
    
    # Save statistics
    stats_path = kb_path / "reprocessing_stats.json"
    import json
    with open(stats_path, 'w') as f:
        json.dump({
            **stats,
            'elapsed_seconds': elapsed_time,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    logger.info(f"\nStatistics saved to: {stats_path}")


if __name__ == "__main__":
    logger.info("Starting PDF reprocessing with enhanced image extraction...")
    logger.info(f"PyMuPDF available: {PYMUPDF_AVAILABLE}")
    logger.info(f"OpenAI available: {OPENAI_AVAILABLE}")
    
    if not PYMUPDF_AVAILABLE:
        logger.error("Cannot proceed without PyMuPDF")
        sys.exit(1)
    
    reprocess_all_pdfs()
