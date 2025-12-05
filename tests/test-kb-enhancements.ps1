# Test Script for Enhanced Knowledge Base Features
# Tests online data fetching, enhanced PDF processing, and performance monitoring

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   KNOWLEDGE BASE ENHANCEMENT TEST SUITE" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8001/api"
$testResults = @()

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Url,
        [object]$Body = $null
    )
    
    Write-Host "`n[TEST] $Name" -ForegroundColor Yellow
    Write-Host "Endpoint: $Method $Url" -ForegroundColor Gray
    
    try {
        $params = @{
            Uri         = $Url
            Method      = $Method
            ContentType = "application/json"
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json -Depth 5)
            Write-Host "Request Body:" -ForegroundColor Gray
            Write-Host ($Body | ConvertTo-Json -Depth 5) -ForegroundColor DarkGray
        }
        
        $startTime = Get-Date
        $response = Invoke-RestMethod @params
        $duration = ((Get-Date) - $startTime).TotalMilliseconds
        
        Write-Host "[PASS] Success (${duration}ms)" -ForegroundColor Green
        Write-Host "Response:" -ForegroundColor Gray
        Write-Host ($response | ConvertTo-Json -Depth 3) -ForegroundColor DarkGray
        
        $script:testResults += @{
            Name     = $Name
            Status   = "PASS"
            Duration = $duration
            Response = $response
        }
        
        return $response
    }
    catch {
        Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Details: $($_.ErrorDetails)" -ForegroundColor DarkRed
        
        $script:testResults += @{
            Name   = $Name
            Status = "FAIL"
            Error  = $_.Exception.Message
        }
        
        return $null
    }
}

Write-Host "`n1. Testing Performance Metrics Endpoint..." -ForegroundColor Cyan
$metrics = Test-Endpoint `
    -Name "Get KB Performance Metrics" `
    -Method "GET" `
    -Url "$baseUrl/medical/knowledge/performance-metrics"

if ($metrics) {
    Write-Host "`nKey Metrics:" -ForegroundColor White
    Write-Host "  - Total Documents: $($metrics.document_manager.total_documents)" -ForegroundColor White
    Write-Host "  - Total Size: $($metrics.document_manager.total_size_mb) MB" -ForegroundColor White
    Write-Host "  - Avg Processing Time: $($metrics.document_manager.performance.avg_processing_time_seconds)s" -ForegroundColor White
    Write-Host "  - Cache Hit Rate: $($metrics.document_manager.performance.cache_hit_rate * 100)%" -ForegroundColor White
    Write-Host "  - PyMuPDF Available: $($metrics.document_manager.engines.pymupdf_available)" -ForegroundColor White
}

Write-Host "`n2. Testing Online Data Fetch (PubMed)..." -ForegroundColor Cyan
$onlineData = Test-Endpoint `
    -Name "Fetch Online Medical Data from PubMed" `
    -Method "POST" `
    -Url "$baseUrl/medical/knowledge/fetch-online-data" `
    -Body @{
    query       = "diabetes treatment guidelines"
    sources     = @("pubmed")
    max_results = 3
    auto_index  = $false
}

if ($onlineData) {
    Write-Host "`nFetch Results:" -ForegroundColor White
    Write-Host "  - Sources Queried: $($onlineData.sources_queried -join ', ')" -ForegroundColor White
    Write-Host "  - Total Documents Found: $($onlineData.total_documents)" -ForegroundColor White
    
    if ($onlineData.results.pubmed) {
        Write-Host "`n  PubMed Papers:" -ForegroundColor White
        $onlineData.results.pubmed | ForEach-Object {
            Write-Host "    - $($_.title)" -ForegroundColor Gray
            Write-Host "      Authors: $($_.authors)" -ForegroundColor DarkGray
            Write-Host "      Journal: $($_.journal)" -ForegroundColor DarkGray
            Write-Host "      URL: $($_.url)" -ForegroundColor DarkGray
        }
    }
}

Write-Host "`n3. Testing Auto-Update Knowledge Base..." -ForegroundColor Cyan
$autoUpdate = Test-Endpoint `
    -Name "Auto-Update KB with Latest Research" `
    -Method "POST" `
    -Url "$baseUrl/medical/knowledge/auto-update" `
    -Body @{
    topics            = @("diabetes", "hypertension")
    sources           = @("pubmed")
    results_per_topic = 2
}

if ($autoUpdate) {
    Write-Host "`nAuto-Update Results:" -ForegroundColor White
    Write-Host "  - Success: $($autoUpdate.success)" -ForegroundColor White
    Write-Host "  - Message: $($autoUpdate.message)" -ForegroundColor White
    Write-Host "  - Topics Searched: $($autoUpdate.update_summary.topics_searched)" -ForegroundColor White
    Write-Host "  - Documents Found: $($autoUpdate.update_summary.documents_found)" -ForegroundColor White
    Write-Host "  - Documents Indexed: $($autoUpdate.update_summary.documents_indexed)" -ForegroundColor White
}

Write-Host "`n4. Testing Enhanced Document Upload..." -ForegroundColor Cyan
Write-Host "Note: This requires a test PDF file. Skipping if not available." -ForegroundColor Gray

$testPdfPath = "test_medical_doc.pdf"
if (Test-Path $testPdfPath) {
    Write-Host "Found test PDF: $testPdfPath" -ForegroundColor Green
    
    try {
        $form = @{
            file        = Get-Item -Path $testPdfPath
            source      = "Test"
            category    = "Test Document"
            description = "Testing enhanced PDF processing"
        }
        
        $startTime = Get-Date
        $uploadResponse = Invoke-RestMethod -Uri "$baseUrl/upload/document" `
            -Method POST -Form $form
        $uploadDuration = ((Get-Date) - $startTime).TotalMilliseconds
        
        Write-Host "[PASS] Document uploaded successfully (${uploadDuration}ms)" -ForegroundColor Green
        Write-Host "Document ID: $($uploadResponse.document.document_id)" -ForegroundColor White
        Write-Host "Processing Time: $($uploadResponse.document.processing_time_seconds)s" -ForegroundColor White
        Write-Host "Text Length: $($uploadResponse.document.text_length) chars" -ForegroundColor White
        Write-Host "Indexed Chunks: $($uploadResponse.document.indexed_chunks)" -ForegroundColor White
        
        $script:testResults += @{
            Name     = "Enhanced Document Upload"
            Status   = "PASS"
            Duration = $uploadDuration
            Response = $uploadResponse
        }
    }
    catch {
        Write-Host "[FAIL] Upload failed: $($_.Exception.Message)" -ForegroundColor Red
        $script:testResults += @{
            Name   = "Enhanced Document Upload"
            Status = "FAIL"
            Error  = $_.Exception.Message
        }
    }
}
else {
    Write-Host "[SKIP] No test PDF file found at $testPdfPath" -ForegroundColor Yellow
    $script:testResults += @{
        Name   = "Enhanced Document Upload"
        Status = "SKIP"
        Reason = "No test file available"
    }
}

Write-Host "`n5. Testing Knowledge Base Statistics..." -ForegroundColor Cyan
$stats = Test-Endpoint `
    -Name "Get KB Statistics" `
    -Method "GET" `
    -Url "$baseUrl/medical/knowledge/statistics"

if ($stats) {
    Write-Host "`nKB Statistics:" -ForegroundColor White
    Write-Host "  - Status: $($stats.status)" -ForegroundColor White
    Write-Host "  - Total Documents: $($stats.total_documents)" -ForegroundColor White
    Write-Host "  - Total Chunks: $($stats.total_chunks)" -ForegroundColor White
    Write-Host "  - Search Mode: $($stats.search_mode)" -ForegroundColor White
}

Write-Host "`n6. Testing Hybrid Search..." -ForegroundColor Cyan
$searchResult = Test-Endpoint `
    -Name "Hybrid Search Query" `
    -Method "POST" `
    -Url "$baseUrl/medical/knowledge/hybrid-search" `
    -Body @{
    query = "diabetes symptoms and treatment"
    top_k = 5
    alpha = 0.7
}

if ($searchResult) {
    Write-Host "`nSearch Results:" -ForegroundColor White
    Write-Host "  - Results Count: $($searchResult.count)" -ForegroundColor White
    Write-Host "  - Search Type: $($searchResult.search_type)" -ForegroundColor White
    Write-Host "  - Alpha: $($searchResult.alpha)" -ForegroundColor White
}

Write-Host "`n7. Testing Cache Operations..." -ForegroundColor Cyan
$cacheResult = Test-Endpoint `
    -Name "Clear Document Cache" `
    -Method "POST" `
    -Url "$baseUrl/medical/knowledge/clear-cache"

if ($cacheResult) {
    Write-Host "`nCache Clear Results:" -ForegroundColor White
    Write-Host "  - Success: $($cacheResult.success)" -ForegroundColor White
    Write-Host "  - Files Cleared: $($cacheResult.files_cleared)" -ForegroundColor White
}

# Summary
Write-Host "`n" -ForegroundColor White
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "              TEST SUMMARY" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

$passed = ($testResults | Where-Object { $_.Status -eq "PASS" }).Count
$failed = ($testResults | Where-Object { $_.Status -eq "FAIL" }).Count
$skipped = ($testResults | Where-Object { $_.Status -eq "SKIP" }).Count
$total = $testResults.Count

Write-Host "Total Tests: $total" -ForegroundColor White
Write-Host "Passed: $passed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Red" })
Write-Host "Skipped: $skipped" -ForegroundColor Yellow

Write-Host "`nDetailed Results:" -ForegroundColor White
$testResults | ForEach-Object {
    $color = switch ($_.Status) {
        "PASS" { "Green" }
        "FAIL" { "Red" }
        "SKIP" { "Yellow" }
    }
    
    Write-Host "  [$($_.Status)] $($_.Name)" -ForegroundColor $color
    
    if ($_.Duration) {
        Write-Host "    Duration: $([math]::Round($_.Duration, 2))ms" -ForegroundColor Gray
    }
    
    if ($_.Error) {
        Write-Host "    Error: $($_.Error)" -ForegroundColor Red
    }
    
    if ($_.Reason) {
        Write-Host "    Reason: $($_.Reason)" -ForegroundColor Gray
    }
}

Write-Host "`n" -ForegroundColor White

if ($failed -eq 0) {
    Write-Host "[OK] All tests passed!" -ForegroundColor Green
}
else {
    Write-Host "[ERROR] Some tests failed. Please check the errors above." -ForegroundColor Red
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
