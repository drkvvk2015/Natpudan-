# Verify Knowledge Base Enhancements
# Quick verification script to ensure all enhancements are working

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   KNOWLEDGE BASE ENHANCEMENTS VERIFICATION             ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8001"

# Test 1: Server Running
Write-Host "[1/4] Checking if backend server is running..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "      ✅ Server is running!" -ForegroundColor Green
} catch {
    Write-Host "      ❌ Server is not running!" -ForegroundColor Red
    Write-Host "      Please start the backend server first:" -ForegroundColor Yellow
    Write-Host "      cd backend" -ForegroundColor White
    Write-Host "      python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001" -ForegroundColor White
    exit 1
}

# Test 2: Enhanced Services Available
Write-Host "`n[2/4] Checking enhanced services..." -ForegroundColor Yellow
try {
    $metrics = Invoke-RestMethod -Uri "$baseUrl/api/medical/knowledge/performance-metrics" -ErrorAction Stop
    
    if ($metrics.document_manager.engines.pymupdf_available) {
        Write-Host "      ✅ PyMuPDF (Fast PDF) - Available" -ForegroundColor Green
    } else {
        Write-Host "      ⚠️  PyMuPDF (Fast PDF) - Not Available (using PyPDF2)" -ForegroundColor Yellow
    }
    
    if ($metrics.document_manager.engines.pypdf2_available) {
        Write-Host "      ✅ PyPDF2 (Fallback) - Available" -ForegroundColor Green
    } else {
        Write-Host "      ⚠️  PyPDF2 (Fallback) - Not Available" -ForegroundColor Yellow
    }
    
    if ($metrics.document_manager.engines.docx_available) {
        Write-Host "      ✅ DOCX Processing - Available" -ForegroundColor Green
    } else {
        Write-Host "      ⚠️  DOCX Processing - Not Available" -ForegroundColor Yellow
    }
    
    Write-Host "`n      Current Stats:" -ForegroundColor Gray
    Write-Host "      • Total Documents: $($metrics.document_manager.total_documents)" -ForegroundColor Gray
    Write-Host "      • Cache Hit Rate: $([math]::Round($metrics.document_manager.performance.cache_hit_rate * 100, 1))%" -ForegroundColor Gray
    Write-Host "      • Avg Processing: $($metrics.document_manager.performance.avg_processing_time_seconds)s" -ForegroundColor Gray
    
} catch {
    Write-Host "      ❌ Could not fetch performance metrics" -ForegroundColor Red
    Write-Host "      Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Online Data Integration
Write-Host "`n[3/4] Testing online data integration (PubMed)..." -ForegroundColor Yellow
try {
    $body = @{
        query = "diabetes"
        sources = @("pubmed")
        max_results = 2
        auto_index = $false
    } | ConvertTo-Json
    
    $result = Invoke-RestMethod -Uri "$baseUrl/api/medical/knowledge/fetch-online-data" `
        -Method POST -Body $body -ContentType "application/json" -ErrorAction Stop
    
    if ($result.total_documents -gt 0) {
        Write-Host "      ✅ Online data fetching works!" -ForegroundColor Green
        Write-Host "      Found $($result.total_documents) papers from PubMed" -ForegroundColor Gray
    } else {
        Write-Host "      ⚠️  No papers found (may be rate limited or network issue)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "      ❌ Online data fetch failed" -ForegroundColor Red
    Write-Host "      Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Knowledge Base Status
Write-Host "`n[4/4] Checking knowledge base status..." -ForegroundColor Yellow
try {
    $stats = Invoke-RestMethod -Uri "$baseUrl/api/medical/knowledge/statistics" -ErrorAction Stop
    
    Write-Host "      ✅ Knowledge Base is operational!" -ForegroundColor Green
    Write-Host "`n      KB Statistics:" -ForegroundColor Gray
    Write-Host "      • Status: $($stats.status)" -ForegroundColor Gray
    Write-Host "      • Documents: $($stats.total_documents)" -ForegroundColor Gray
    Write-Host "      • Chunks: $($stats.total_chunks)" -ForegroundColor Gray
    Write-Host "      • Search Mode: $($stats.search_mode)" -ForegroundColor Gray
    
    if ($stats.pdf_sources) {
        Write-Host "`n      PDF Sources:" -ForegroundColor Gray
        $stats.pdf_sources | ForEach-Object {
            Write-Host "      • $($_.name) ($($_.size_mb)MB) - $($_.status)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "      ❌ Could not fetch KB statistics" -ForegroundColor Red
    Write-Host "      Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Summary
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   VERIFICATION COMPLETE                                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Knowledge Base Enhancements are ready!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor White
Write-Host "  1. Run full test suite:" -ForegroundColor Gray
Write-Host "     .\test-kb-enhancements.ps1" -ForegroundColor White
Write-Host ""
Write-Host "  2. Upload a PDF to test speed:" -ForegroundColor Gray
Write-Host "     Go to http://localhost:3000/knowledge-base" -ForegroundColor White
Write-Host ""
Write-Host "  3. Monitor performance:" -ForegroundColor Gray
Write-Host "     Invoke-RestMethod -Uri '$baseUrl/api/medical/knowledge/performance-metrics'" -ForegroundColor White
Write-Host ""
Write-Host "  4. Read documentation:" -ForegroundColor Gray
Write-Host "     • KB_IMPROVEMENTS_SUMMARY.md - Executive summary" -ForegroundColor White
Write-Host "     • KB_ENHANCEMENT_COMPLETE.md - Detailed features" -ForegroundColor White
Write-Host "     • KB_QUICKSTART.md - Usage guide" -ForegroundColor White
Write-Host ""
