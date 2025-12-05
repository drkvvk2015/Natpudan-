# OCR & Image Extraction Implementation - Complete

## What's Been Implemented 

### 1. Enhanced PDF Processing with OCR
- **Smart Detection**: Automatically detects text-based vs image-based PDFs
- **OCR Fallback**: If PDF has < 50 chars/page, attempts OCR extraction
- **Image Extraction**: Saves all images with metadata and indexing
- **Hybrid Support**: Works with partially-scanned PDFs

### 2. Image Management System
- **Database Model**: `ExtractedImage` table for tracking all images
- **Metadata Storage**: JSON files alongside images with full context
- **Indexed by**: document_id, page_number, image_index
- **Storage**: `data/knowledge_base/images/` directory
- **Unique IDs**: Hash-based naming to prevent duplicates

### 3. API Enhancements

#### Upload Endpoint (`POST /api/medical/knowledge/upload`)
New parameters:
- `extract_images=True` (default) - Extract and save images
- `ocr_enabled=True` (default) - Enable OCR for scanned PDFs

Response includes:
```json
{
  "images_extracted": 15,
  "extraction_method": "text"|"ocr"|"hybrid",
  "info": "Extracted via ocr. 15 images saved..."
}
```

#### OCR Status Endpoint (`GET /api/medical/knowledge/ocr-status`)
Check setup status:
```json
{
  "status": "ready"|"needs_setup",
  "ocr_available": false,
  "components": {
    "pytesseract": "installed",
    "pdf2image": "installed",
    "tesseract_ocr": "not_installed",
    "poppler": "available"
  },
  "setup_instructions": [...]
}
```

### 4. Database Schema

**New Table: `extracted_images`**
```sql
CREATE TABLE extracted_images (
    id INTEGER PRIMARY KEY,
    image_id TEXT UNIQUE,
    document_id TEXT REFERENCES knowledge_documents(document_id),
    filename TEXT,
    file_path TEXT,
    page_number INTEGER,
    image_index INTEGER,
    xref INTEGER,
    extension TEXT,
    size_bytes INTEGER,
    width INTEGER,
    height INTEGER,
    ocr_text TEXT,      -- For future OCR on images
    caption TEXT,        -- For future AI captioning
    tags JSON,           -- For future classification
    extracted_at DATETIME
)
```

## Current Setup Status

###  Installed
- Python libraries: `pytesseract`, `pdf2image`, `pillow`
- PDF processing: PyMuPDF (fitz)
- Image handling: PIL/Pillow

###  Missing (for full OCR)
1. **Tesseract OCR Engine** - Required for OCR processing
2. **Poppler binaries** - Already installed (pdf2image working)

## How to Complete Setup

### Option 1: Quick Setup (Windows)

**Step 1: Install Tesseract OCR**
```powershell
# Download installer
# https://github.com/UB-Mannheim/tesseract/wiki

# Run: tesseract-ocr-w64-setup-5.3.3.20231005.exe
# Default location: C:\Program Files\Tesseract-OCR
```

**Step 2: Add to PATH**
```powershell
# Add to system PATH:
$env:Path += ";C:\Program Files\Tesseract-OCR"

# Or set permanently:
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\Tesseract-OCR", [EnvironmentVariableTarget]::Machine)
```

**Step 3: Verify Installation**
```powershell
tesseract --version
# Should show: tesseract 5.3.3
```

**Step 4: Restart Backend**
```powershell
# Stop current backend (Ctrl+C)
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Step 5: Test OCR**
```powershell
# Check status
curl http://127.0.0.1:8000/api/medical/knowledge/ocr-status

# Upload a scanned PDF - it will auto-apply OCR
```

### Option 2: Manual Configuration

If Tesseract is installed but not in PATH:

```python
# In backend/.env or set environment variable:
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

## How It Works

### Text-Based PDF (Normal)
```
1. User uploads PDF
2. System extracts text using PyMuPDF (fast)
3. System extracts images  saves to images/ folder
4. Returns immediately with document ID
5. Background task creates embeddings
```

### Scanned PDF (with OCR)
```
1. User uploads PDF
2. System tries PyMuPDF  gets < 50 chars/page
3. System detects: "This needs OCR"
4. Converts PDF pages to images (pdf2image + poppler)
5. Runs Tesseract OCR on each image
6. Extracts text from OCR results
7. System extracts images  saves to images/ folder
8. Returns with document ID + OCR note
9. Background task creates embeddings
```

### Image Extraction (Always)
```
For each page:
  1. Detect embedded images using PyMuPDF
  2. Extract image bytes
  3. Generate unique ID: {document_id}_{page}_{index}_{hash}.{ext}
  4. Save to: data/knowledge_base/images/
  5. Create metadata JSON:
     - page number
     - image index
     - dimensions
     - document reference
  6. Store in database: extracted_images table
```

## Image Metadata Example

**File**: `data/knowledge_base/images/abc123_CardiacAtlas_p15_img1_a3f2b1c8.png`

**Metadata JSON** (same name + .json):
```json
{
  "filename": "abc123_CardiacAtlas_p15_img1_a3f2b1c8.png",
  "path": "/path/to/images/abc123_CardiacAtlas_p15_img1_a3f2b1c8.png",
  "page": 15,
  "index": 1,
  "xref": 1523,
  "extension": "png",
  "size_bytes": 245830,
  "document_id": "abc123",
  "pdf_name": "CardiacAtlas",
  "extracted_at": "2025-12-05T16:45:30"
}
```

## Testing the System

### Test 1: Check Setup Status
```bash
curl http://127.0.0.1:8000/api/medical/knowledge/ocr-status
```

Expected (before Tesseract):
```json
{
  "status": "needs_setup",
  "ocr_available": false,
  "setup_instructions": [
    {
      "component": "Tesseract OCR",
      "status": "missing",
      "windows_install": "Download from https://github.com/UB-Mannheim/tesseract/wiki"
    }
  ]
}
```

Expected (after Tesseract):
```json
{
  "status": "ready",
  "ocr_available": true,
  "capabilities": {
    "text_extraction": true,
    "image_extraction": true,
    "ocr_processing": true,
    "scanned_pdf_support": true
  }
}
```

### Test 2: Upload Text-Based PDF
```bash
# Via frontend Upload page
# Or via curl:
curl -X POST http://127.0.0.1:8000/api/medical/knowledge/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@medical_book.pdf" \
  -F "extract_images=true" \
  -F "ocr_enabled=true"
```

Expected response:
```json
{
  "filename": "medical_book.pdf",
  "status": "success",
  "extraction_method": "text",
  "images_extracted": 42,
  "chunks": 125,
  "characters": 285420,
  "info": "Extracted via text. 42 images saved. 125 chunks queued."
}
```

### Test 3: Upload Scanned PDF (After OCR Setup)
Same command, but with scanned PDF:

Expected response:
```json
{
  "filename": "scanned_textbook.pdf",
  "status": "success",
  "extraction_method": "ocr",
  "images_extracted": 38,
  "chunks": 95,
  "characters": 178340,
  "info": "Extracted via ocr. 38 images saved. 95 chunks queued."
}
```

### Test 4: Check Extracted Images
```bash
# List images directory
ls data/knowledge_base/images/

# Should show:
# {doc_id}_{filename}_p{page}_img{index}_{hash}.{ext}
# Plus corresponding .json metadata files
```

### Test 5: Query Database
```sql
-- View extracted images
SELECT image_id, document_id, filename, page_number, size_bytes 
FROM extracted_images 
ORDER BY extracted_at DESC 
LIMIT 10;

-- Count images per document
SELECT document_id, COUNT(*) as image_count
FROM extracted_images
GROUP BY document_id;
```

## Performance Notes

### Text-Based PDF
- **Speed**: ~100-500 pages/second
- **Accuracy**: 100% (native text)
- **CPU**: Low
- **Time**: Few seconds even for 1000-page books

### OCR-Based PDF (Scanned)
- **Speed**: ~1-3 pages/second (at 300 DPI)
- **Accuracy**: 90-95% (depends on scan quality)
- **CPU**: High (Tesseract uses multiple cores)
- **Time**: 5-30 seconds per page
  - 100-page book: 8-50 minutes
  - 500-page book: 40-250 minutes

**Recommendation**: For scanned PDFs:
1. Use batch uploads during off-hours
2. Monitor CPU usage
3. Consider cloud OCR services for large volumes (AWS Textract, Azure Computer Vision)

## Future Enhancements (Already Prepared)

### 1. Image OCR
The `ocr_text` column in `extracted_images` table is ready for:
- Running OCR on extracted images
- Storing image text separately
- Searching within diagram text

### 2. AI Image Captioning
The `caption` column is ready for:
- OpenAI Vision API integration
- Automatic medical image description
- Enhanced search with image context

### 3. Image Classification
The `tags` JSON column is ready for:
- Automatic tagging (diagram, chart, photo, illustration)
- Medical classification (X-ray, CT scan, ECG, etc.)
- Filtering images by type

## Troubleshooting

### Issue: "Tesseract not found"
**Solution**: Verify PATH or set `TESSERACT_CMD` environment variable

### Issue: OCR is slow
**Normal**: OCR takes time. For 100+ page scans, use batch processing

### Issue: OCR text quality is poor
**Solutions**:
- Increase DPI in pdf2image: `convert_from_path(pdf, dpi=600)`
- Pre-process images (contrast, denoise)
- Use higher quality scans

### Issue: Images folder getting large
**Solutions**:
- Images are already compressed (PNG/JPEG from PDF)
- Implement cleanup for old/unused images
- Use cloud storage (S3, Azure Blob)

## Files Modified/Created

| File | Status | Purpose |
|------|--------|---------|
| `backend/app/services/pdf_ocr_processor.py` |  Created | OCR + image extraction engine |
| `backend/app/models.py` |  Updated | Added ExtractedImage model, JSON import |
| `backend/app/api/knowledge_base.py` |  Updated | Integrated OCR processor, added OCR status endpoint |
| `data/knowledge_base/images/` |  Created | Image storage directory |
| Database: `extracted_images` table |  Created | Image metadata storage |

## Summary

**System Status**: 
-  Image extraction: **WORKING**
-  Text extraction: **WORKING**
-  OCR processing: **READY** (needs Tesseract installation)
-  Database models: **CREATED**
-  API endpoints: **READY**

**To Enable Full OCR**:
1. Download Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to: `C:\Program Files\Tesseract-OCR`
3. Add to PATH
4. Restart backend
5. Test with: `curl http://127.0.0.1:8000/api/medical/knowledge/ocr-status`

**Already Working**:
- Upload PDFs  extracts text + images
- Images saved to `/images/` with metadata
- Metadata stored in database
- Setup status endpoint shows what's missing
- Graceful fallback if Tesseract not installed
