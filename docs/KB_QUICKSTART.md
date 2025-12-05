# [EMOJI] Quick Start Guide - Enhanced Knowledge Base

## Prerequisites
- Python 3.9+ with all requirements installed
- Node.js 18+ (for frontend)
- OpenAI API key configured

## Start Backend with Enhancements

```powershell
# Navigate to backend
cd backend

# Ensure all dependencies are installed
pip install -r requirements.txt

# Start server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

## Verify Enhancements

### 1. Check Performance Metrics
```powershell
# Open PowerShell and run:
Invoke-RestMethod -Uri "http://localhost:8001/api/medical/knowledge/performance-metrics"
```

**Expected Output:**
```json
{
  "success": true,
  "document_manager": {
    "engines": {
      "pymupdf_available": true,
      "pypdf2_available": true,
      "docx_available": true
    },
    "performance": {
      "avg_processing_time_seconds": 0.0,
      "cache_hit_rate": 0.0
    }
  }
}
```

### 2. Test Online Data Fetching
```powershell
# Fetch latest diabetes research
$body = @{
    query = "diabetes"
    sources = @("pubmed")
    max_results = 5
    auto_index = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/api/medical/knowledge/fetch-online-data" `
    -Method POST -Body $body -ContentType "application/json"
```

### 3. Run Full Test Suite
```powershell
# From project root
.\test-kb-enhancements.ps1
```

## Usage Examples

### Upload PDF (Enhanced Processing)
```powershell
# Much faster with PyMuPDF + caching
$form = @{
    file = Get-Item "medical_report.pdf"
    source = "Hospital"
    category = "Medical Report"
}

$response = Invoke-RestMethod -Uri "http://localhost:8001/api/upload/document" `
    -Method POST -Form $form

Write-Host "Processing time: $($response.document.processing_time_seconds)s"
Write-Host "Text extracted: $($response.document.text_length) chars"
```

### Auto-Update Knowledge Base Daily
```powershell
# Add to scheduled task
$body = @{
    topics = @("diabetes", "hypertension", "covid-19", "cardiology")
    sources = @("pubmed")
    results_per_topic = 10
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/api/medical/knowledge/auto-update" `
    -Method POST -Body $body -ContentType "application/json"
```

### Monitor Performance
```powershell
# Check cache performance
$metrics = Invoke-RestMethod -Uri "http://localhost:8001/api/medical/knowledge/performance-metrics"

Write-Host "Cache Hit Rate: $($metrics.document_manager.performance.cache_hit_rate * 100)%"
Write-Host "Average Processing Time: $($metrics.document_manager.performance.avg_processing_time_seconds)s"
```

## Performance Tips

### 1. Enable Caching
Cache is enabled by default. Files are cached in `backend/data/document_cache/`

### 2. Use PyMuPDF
Already configured as primary PDF engine (5-10x faster than PyPDF2)

### 3. Async Processing
All document uploads are processed asynchronously - no blocking

### 4. Batch Processing
Upload multiple documents at once for better throughput

### 5. Regular Cache Maintenance
```powershell
# Clear cache if it gets too large (>1GB)
Invoke-RestMethod -Uri "http://localhost:8001/api/medical/knowledge/clear-cache" -Method POST
```

## Troubleshooting

### Issue: PDF Processing Still Slow
**Solution:**
1. Check if PyMuPDF is installed: `pip list | findstr PyMuPDF`
2. If missing: `pip install PyMuPDF`
3. Restart backend server

### Issue: Online Data Fetch Fails
**Solution:**
1. Check internet connection
2. PubMed API has rate limits (3 requests/second)
3. Try smaller `max_results` value

### Issue: Out of Memory
**Solution:**
1. Reduce `max_workers` in `enhanced_document_manager.py`
2. Process smaller batches
3. Clear cache regularly

### Issue: Cache Not Working
**Solution:**
1. Check `backend/data/document_cache/` exists
2. Check write permissions
3. Verify `enable_cache=True` in manager init

## Monitoring & Alerts

### Key Metrics to Watch
1. **Average Processing Time** - Should be <2s for most PDFs
2. **Cache Hit Rate** - Target >60% after initial uploads
3. **Error Rate** - Should be <1%
4. **KB Growth** - Monitor total_documents and total_chunks

### Set Up Monitoring
```powershell
# Create a monitoring script
while ($true) {
    $metrics = Invoke-RestMethod -Uri "http://localhost:8001/api/medical/knowledge/performance-metrics"
    
    Write-Host "$(Get-Date -Format 'HH:mm:ss')" -NoNewline
    Write-Host " | Docs: $($metrics.document_manager.total_documents)" -NoNewline
    Write-Host " | Avg Time: $($metrics.document_manager.performance.avg_processing_time_seconds)s" -NoNewline
    Write-Host " | Cache: $($metrics.document_manager.performance.cache_hit_rate * 100)%" -NoNewline
    Write-Host " | Errors: $($metrics.document_manager.performance.errors)"
    
    Start-Sleep -Seconds 60
}
```

## Integration with Frontend

### Update KnowledgeBase.tsx
```typescript
// Add button for online data fetch
const fetchOnlineData = async () => {
  try {
    const response = await axios.post('/api/medical/knowledge/fetch-online-data', {
      query: searchQuery,
      sources: ['pubmed'],
      max_results: 10,
      auto_index: true
    });
    
    alert(`Found ${response.data.total_documents} online documents and indexed them!`);
  } catch (error) {
    console.error('Failed to fetch online data:', error);
  }
};
```

## Best Practices

### 1. Document Uploads
- [OK] Use descriptive filenames
- [OK] Add metadata (source, category, description)
- [OK] Monitor processing times
- [OK] Check indexed_chunks count

### 2. Online Data
- [OK] Schedule auto-updates during off-peak hours
- [OK] Use specific medical topics
- [OK] Set reasonable max_results (5-10)
- [OK] Enable auto_index for automatic integration

### 3. Performance
- [OK] Keep cache enabled
- [OK] Monitor cache hit rate
- [OK] Clear cache monthly or when >1GB
- [OK] Use async operations

### 4. Error Handling
- [OK] Check response.success field
- [OK] Log errors with details
- [OK] Implement retry logic for uploads
- [OK] Handle partial extraction gracefully

## Next Steps

1. **Test Everything**
   ```powershell
   .\test-kb-enhancements.ps1
   ```

2. **Upload Test Documents**
   - Upload a small PDF (verify speed)
   - Upload the same PDF again (verify cache)
   - Check performance metrics

3. **Fetch Online Data**
   - Try different medical topics
   - Verify auto-indexing works
   - Check knowledge base statistics

4. **Monitor Performance**
   - Set up periodic metric checks
   - Watch for errors
   - Optimize based on metrics

5. **Production Deployment**
   - Configure rate limiting
   - Set up backup schedule
   - Monitor logs
   - Scale as needed

## Support

For issues or questions:
1. Check logs: `backend/logs/`
2. Review metrics: `/api/medical/knowledge/performance-metrics`
3. Run test suite: `test-kb-enhancements.ps1`
4. Check documentation: `KB_ENHANCEMENT_COMPLETE.md`

---

**[EMOJI] You're all set! The enhanced Knowledge Base is ready for production use.**
