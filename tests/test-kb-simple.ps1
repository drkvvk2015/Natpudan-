# Simple Knowledge Base Test Script
$baseUrl = "http://127.0.0.1:8000"

Write-Host "=== Testing Knowledge Base ===" -ForegroundColor Cyan

# Test 1: Health Check
Write-Host "`n1. Testing Health Endpoint..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
    Write-Host "   [OK] Health: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Statistics (before upload)
Write-Host "`n2. Testing Statistics Endpoint (before upload)..." -ForegroundColor Yellow
try {
    $stats = Invoke-RestMethod -Uri "$baseUrl/api/medical/knowledge/statistics" -Method Get
    Write-Host "   Total Documents: $($stats.total_documents)" -ForegroundColor Green
    Write-Host "   Total Chunks: $($stats.total_chunks)" -ForegroundColor Green
    Write-Host "   Knowledge Level: $($stats.knowledge_level)" -ForegroundColor Green
    Write-Host "   PDF Sources: $($stats.pdf_sources.Count)" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Statistics failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Upload a PDF
Write-Host "`n3. Uploading a PDF from medical_books..." -ForegroundColor Yellow
$medicalBooksDir = Join-Path $PSScriptRoot "backend\data\medical_books"
$pdfFiles = Get-ChildItem -Path $medicalBooksDir -Filter "*.pdf" -ErrorAction SilentlyContinue

if ($pdfFiles) {
    $firstPdf = $pdfFiles[0]
    $sizeMB = [math]::Round($firstPdf.Length/1MB, 2)
    Write-Host "   Found: $($firstPdf.Name) ($sizeMB MB)" -ForegroundColor Gray
    
    try {
        # Create multipart form data
        $boundary = [System.Guid]::NewGuid().ToString()
        $fileBin = [System.IO.File]::ReadAllBytes($firstPdf.FullName)
        
        $bodyLines = @(
            "--$boundary",
            "Content-Disposition: form-data; name=`"file`"; filename=`"$($firstPdf.Name)`"",
            "Content-Type: application/pdf",
            "",
            [System.Text.Encoding]::GetEncoding("iso-8859-1").GetString($fileBin),
            "--$boundary--"
        )
        
        $body = $bodyLines -join "`r`n"
        
        $uploadResult = Invoke-RestMethod -Uri "$baseUrl/api/upload/document" `
            -Method Post `
            -ContentType "multipart/form-data; boundary=$boundary" `
            -Body $body
            
        Write-Host "   [OK] Upload successful!" -ForegroundColor Green
        Write-Host "   Document ID: $($uploadResult.document_id)" -ForegroundColor Gray
        Write-Host "   Chunks: $($uploadResult.chunks_created)" -ForegroundColor Gray
    } catch {
        Write-Host "   ✗ Upload failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "   ✗ No PDF files found in $medicalBooksDir" -ForegroundColor Red
}

# Test 4: Statistics (after upload)
Write-Host "`n4. Testing Statistics Endpoint (after upload)..." -ForegroundColor Yellow
try {
    $statsAfter = Invoke-RestMethod -Uri "$baseUrl/api/medical/knowledge/statistics" -Method Get
    Write-Host "   Total Documents: $($statsAfter.total_documents)" -ForegroundColor Green
    Write-Host "   Total Chunks: $($statsAfter.total_chunks)" -ForegroundColor Green
    Write-Host "   Knowledge Level: $($statsAfter.knowledge_level)" -ForegroundColor Green
    if ($statsAfter.pdf_sources) {
        Write-Host "   PDF Sources:" -ForegroundColor Green
        foreach ($pdf in $statsAfter.pdf_sources) {
            Write-Host "     - $($pdf.name) ($($pdf.size_mb) MB)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "   ✗ Statistics failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Search for "fever"
Write-Host "`n5. Searching for 'fever'..." -ForegroundColor Yellow
try {
    $searchBody = @{
        query = "fever"
        top_k = 5
    } | ConvertTo-Json
    
    $searchResults = Invoke-RestMethod -Uri "$baseUrl/api/medical/knowledge/search" `
        -Method Post `
        -ContentType "application/json" `
        -Body $searchBody
    
    Write-Host "   [OK] Found $($searchResults.results.Count) results" -ForegroundColor Green
    
    foreach ($i in 0..([Math]::Min(2, $searchResults.results.Count - 1))) {
        $result = $searchResults.results[$i]
        Write-Host "`n   Result $($i + 1):" -ForegroundColor Cyan
        Write-Host "     Source: $($result.metadata.source)" -ForegroundColor Gray
        Write-Host "     Score: $([math]::Round($result.score, 4))" -ForegroundColor Gray
        Write-Host "     Content: $($result.content.Substring(0, [Math]::Min(150, $result.content.Length)))..." -ForegroundColor Gray
    }
} catch {
    Write-Host "   ✗ Search failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan
