# How to Upload Medical PDFs to Knowledge Base

## You have 4 PDF files to upload:
1. **Crash Course General Medicine.pdf** (8.93 MB)
2. **Crash Course SBAs and EMQs in Medicine and Surgery.pdf** (5.38 MB)
3. **DRUG OF CHOICE (1).pdf** (5.60 MB)
4. **Pharmacological_classification_of_Drugs_1727170824.pdf** (2.90 MB)

**Total Size: ~23 MB** [OK] (Well within limits)

---

## Method 1: Using PowerShell Script (Recommended)

### Step 1: Place PDF Files
Copy your 4 PDF files to this directory:
```
D:\Users\CNSHO\Documents\GitHub\Natpudan-\
```

### Step 2: Ensure Backend is Running
```powershell
.\start-backend.ps1
```
Wait until you see "Knowledge base initialized successfully" and "Application startup complete"

### Step 3: Run Upload Script
```powershell
.\upload-medical-pdfs.ps1
```

The script will:
- [OK] Check backend connectivity
- [OK] Authenticate with your credentials
- [OK] Upload all PDFs automatically
- [OK] Process and index content
- [OK] Show detailed progress

---

## Method 2: Using the Web Interface

### Step 1: Navigate to Knowledge Base Page
1. Open browser: http://localhost:5173
2. Login with your credentials
3. Go to **Knowledge Base** page from the sidebar

### Step 2: Upload Files
1. Click **"Upload Documents"** button
2. Select all 4 PDF files
3. Choose processing options:
   - [OK] **Use Full Content** (Recommended for medical textbooks)
   - Chunk Size: 1000 characters
4. Click **Upload**

### Step 3: Verify Upload
The system will:
- Extract text from PDFs
- Create semantic embeddings
- Index for fast retrieval
- Show success confirmation with statistics

---

## Method 3: Using cURL (Advanced)

### Get Authentication Token
```bash
curl -X POST http://127.0.0.1:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"your-email@example.com","password":"your-password"}'
```

### Upload PDF
```bash
curl -X POST http://127.0.0.1:8001/api/knowledge-base/upload \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "files=@Crash Course General Medicine.pdf" \
  -F "use_full_content=true" \
  -F "chunk_size=1000"
```

Repeat for each PDF file.

---

## Expected Processing Time

| File | Size | Est. Time |
|------|------|-----------|
| Crash Course General Medicine | 8.93 MB | ~30-45 sec |
| Crash Course SBAs and EMQs | 5.38 MB | ~20-30 sec |
| DRUG OF CHOICE | 5.60 MB | ~20-30 sec |
| Pharmacological Classification | 2.90 MB | ~10-15 sec |

**Total: ~2-3 minutes** for all files

---

## What Happens After Upload?

1. **Text Extraction**: PyMuPDF extracts text from each PDF page
2. **Semantic Analysis**: Sentence Transformers creates embeddings
3. **Vector Storage**: FAISS indexes vectors for fast similarity search
4. **BM25 Indexing**: Keyword search index created
5. **Hybrid Search**: Combined semantic + keyword retrieval

---

## Verify Upload Success

### Check Knowledge Base Statistics
```bash
curl http://127.0.0.1:8001/api/knowledge-base/statistics
```

Should show increased:
- [OK] `total_documents`: +4 documents
- [OK] `total_chunks`: Depends on chunking
- [OK] `total_characters`: ~23 MB of text

### Test Search
Try searching for medical topics:
```bash
curl -X POST http://127.0.0.1:8001/api/knowledge-base/search \
  -H "Content-Type: application/json" \
  -d '{"query":"diabetes treatment guidelines","top_k":5}'
```

---

## Troubleshooting

### Error: "File too large"
- **Cause**: Individual file > 200 MB
- **Solution**: Your files are all < 10 MB, this shouldn't happen

### Error: "Authentication failed"
- **Cause**: Invalid credentials or expired token
- **Solution**: Login again to get fresh token

### Error: "No text extracted"
- **Cause**: PDF is scanned image without OCR
- **Solution**: Enable OCR in processing options (slower but works)

### Error: "Backend not running"
- **Cause**: FastAPI server not started
- **Solution**: Run `.\start-backend.ps1` first

---

## File Placement Quick Reference

Put your PDFs here (same directory as this guide):
```
D:\Users\CNSHO\Documents\GitHub\Natpudan-\
   Crash Course General Medicine.pdf            Place here
   Crash Course SBAs and EMQs in Medicine and Surgery.pdf   Place here
   DRUG OF CHOICE (1).pdf                       Place here
   Pharmacological_classification_of_Drugs_1727170824.pdf   Place here
   upload-medical-pdfs.ps1                      Run this
```

---

## Quick Start Command

```powershell
# One-liner to upload all PDFs in current directory
.\upload-medical-pdfs.ps1
```

**Enter your email and password when prompted, then wait for completion!**

---

## After Upload

Your AI assistant will now have access to:
- [OK] General Medicine knowledge (Crash Course)
- [OK] Clinical scenarios and questions (SBAs & EMQs)
- [OK] Drug therapy guidelines (Drug of Choice)
- [OK] Pharmacological classifications

**Test it**: Go to Chat page and ask:
> "What are the first-line drugs for hypertension?"

The AI should now provide answers based on your uploaded textbooks! [EMOJI]
