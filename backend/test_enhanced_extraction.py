"""
Test Enhanced KB Processor on a single PDF
Quick validation before full reprocessing
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.enhanced_kb_processor import EnhancedKBProcessor, PYMUPDF_AVAILABLE, OPENAI_AVAILABLE

def test_extraction():
    """Test image extraction on first available PDF"""
    
    if not PYMUPDF_AVAILABLE:
        print("[ERROR] PyMuPDF not available")
        return
    
    kb_path = Path("data/knowledge_base")
    pdf_files = list(kb_path.glob("*.pdf"))
    
    if not pdf_files:
        print("[ERROR] No PDF files found")
        return
    
    # Test with first small PDF
    test_pdf = sorted(pdf_files, key=lambda f: f.stat().st_size)[0]
    print(f"[SEARCH] Testing with: {test_pdf.name}")
    print(f"   Size: {test_pdf.stat().st_size / 1024:.1f} KB")
    
    processor = EnhancedKBProcessor(storage_dir=str(kb_path))
    
    print("\n[DOC] Extracting content...")
    result = processor.extract_text_and_images(str(test_pdf))
    
    if 'error' in result:
        print(f"[ERROR] Error: {result['error']}")
        return
    
    # Display results
    metadata = result.get('metadata', {})
    text_chunks = result.get('text_chunks', [])
    images = result.get('images', [])
    
    print("\n[OK] Extraction successful!")
    print(f"   Pages: {metadata.get('pages', 0)}")
    print(f"   Text chunks: {len(text_chunks)}")
    print(f"   Images: {len(images)}")
    
    if text_chunks:
        print(f"\n[NOTE] Sample text (first 200 chars):")
        sample = text_chunks[0].get('text', '')[:200]
        print(f"   {sample}...")
    
    if images:
        print(f"\n[IMAGE]  Image details:")
        for idx, img in enumerate(images[:3], 1):  # Show first 3
            print(f"   Image {idx}:")
            print(f"     Page: {img.get('page')}")
            print(f"     Size: {img.get('size', 0) / 1024:.1f} KB")
            print(f"     Format: {img.get('format')}")
            print(f"     Hash: {img.get('hash')[:16]}...")
            if img.get('caption'):
                print(f"     Caption: {img.get('caption')[:50]}...")
        
        if len(images) > 3:
            print(f"   ... and {len(images) - 3} more images")
        
        # Test AI description if available
        if OPENAI_AVAILABLE and processor.client:
            print(f"\n[AI] Testing AI image description...")
            first_image = images[0]['image_data']
            description = processor.describe_image_with_ai(first_image)
            print(f"   Description: {description[:200]}...")
        else:
            print(f"\n[WARNING]  OpenAI not available - skipping AI descriptions")
    
    print("\n[OK] Test complete!")

if __name__ == "__main__":
    print("Testing Enhanced KB Processor\n")
    print(f"PyMuPDF: {'[OK]' if PYMUPDF_AVAILABLE else '[ERROR]'}")
    print(f"OpenAI: {'[OK]' if OPENAI_AVAILABLE else '[ERROR]'}")
    print()
    test_extraction()
