# Process Medical Books - Index all PDFs in medical_books directory
# This creates embeddings and builds the FAISS index for semantic search

Write-Host "`n" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host " Processing Medical Books into Knowledge Base" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

$BASE_URL = "http://127.0.0.1:8000"

# Check backend health
Write-Host "[1/5] Checking backend status..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$BASE_URL/health" -ErrorAction Stop
    Write-Host "  ✓ Backend is $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Backend is offline. Please start the backend first." -ForegroundColor Red
    Write-Host "  Run: .\start-backend.ps1" -ForegroundColor Yellow
    exit 1
}

# Login to get token (required for upload)
Write-Host "`n[2/5] Logging in..." -ForegroundColor Yellow
$loginBody = @{
    email = "admin@example.com"
    password = "admin123"
} | ConvertTo-Json

try {
    $login = Invoke-RestMethod -Uri "$BASE_URL/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json" -ErrorAction Stop
    $TOKEN = $login.access_token
    Write-Host "  ✓ Logged in as admin" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Login failed. Using default credentials." -ForegroundColor Yellow
    Write-Host "  If this fails, create admin user first with: .\create-admin.ps1" -ForegroundColor Gray
    exit 1
}

# Check current KB status
Write-Host "`n[3/5] Checking current knowledge base status..." -ForegroundColor Yellow
try {
    $stats = Invoke-RestMethod -Uri "$BASE_URL/api/medical/knowledge/statistics" -ErrorAction Stop
    Write-Host "  📊 Current Status:" -ForegroundColor Cyan
    Write-Host "     - Documents indexed: $($stats.total_documents)" -ForegroundColor White
    Write-Host "     - Total chunks: $($stats.total_chunks)" -ForegroundColor White
    Write-Host "     - Knowledge level: $($stats.knowledge_level)" -ForegroundColor White
    Write-Host "     - Model loaded: $($stats.model_loaded)" -ForegroundColor White
    Write-Host "     - Medical books available: $($stats.medical_books_count)" -ForegroundColor White
    Write-Host "     - PDF sources: $($stats.pdf_sources.Count)" -ForegroundColor White
} catch {
    Write-Host "  ⚠ Could not get KB stats" -ForegroundColor Yellow
}

# Get list of PDFs to process
Write-Host "`n[4/5] Finding PDFs to process..." -ForegroundColor Yellow
$medicalBooksDir = "F:\Software\android apps\Natpudan-\backend\data\medical_books"

if (!(Test-Path $medicalBooksDir)) {
    Write-Host "  ✗ Medical books directory not found: $medicalBooksDir" -ForegroundColor Red
    exit 1
}

$pdfFiles = Get-ChildItem -Path $medicalBooksDir -Filter "*.pdf" -File
Write-Host "  ✓ Found $($pdfFiles.Count) PDF files" -ForegroundColor Green

if ($pdfFiles.Count -eq 0) {
    Write-Host "  ⚠ No PDF files to process" -ForegroundColor Yellow
    exit 0
}

# Show some file examples
Write-Host "`n  Sample files:" -ForegroundColor Cyan
$pdfFiles | Select-Object -First 5 | ForEach-Object {
    $sizeMB = [math]::Round($_.Length / 1MB, 2)
    Write-Host "    - $($_.Name) ($sizeMB MB)" -ForegroundColor Gray
}

if ($pdfFiles.Count -gt 5) {
    Write-Host "    ... and $($pdfFiles.Count - 5) more files" -ForegroundColor Gray
}

# Process PDFs
Write-Host "`n[5/5] Processing PDFs..." -ForegroundColor Yellow
Write-Host "  ⏳ This will take several minutes (large files + embeddings generation)" -ForegroundColor Yellow
Write-Host "  📝 Progress will be shown below:`n" -ForegroundColor Gray

$headers = @{
    "Authorization" = "Bearer $TOKEN"
}

$processedCount = 0
$failedCount = 0
$startTime = Get-Date

foreach ($pdf in $pdfFiles) {
    $fileName = $pdf.Name
    $sizeMB = [math]::Round($pdf.Length / 1MB, 2)
    
    Write-Host "  Processing: $fileName ($sizeMB MB)..." -ForegroundColor Cyan -NoNewline
    
    try {
        # Use multipart/form-data upload
        $boundary = [System.Guid]::NewGuid().ToString()
        $filePath = $pdf.FullName
        
        # Build multipart body
        $LF = "`r`n"
        $bodyLines = (
            "--$boundary",
            "Content-Disposition: form-data; name=`"file`"; filename=`"$fileName`"",
            "Content-Type: application/pdf",
            "",
            [System.IO.File]::ReadAllText($filePath),
            "--$boundary--"
        ) -join $LF
        
        $uploadHeaders = @{
            "Authorization" = "Bearer $TOKEN"
            "Content-Type" = "multipart/form-data; boundary=$boundary"
        }
        
        # Upload with timeout (large files take time)
        $response = Invoke-RestMethod -Uri "$BASE_URL/api/medical/knowledge/upload" `
            -Method Post `
            -Headers $uploadHeaders `
            -Body $bodyLines `
            -TimeoutSec 300 `
            -ErrorAction Stop
        
        Write-Host " ✓ " -ForegroundColor Green -NoNewline
        Write-Host "$($response.status)" -ForegroundColor Gray
        $processedCount++
        
        # Small delay to avoid overwhelming the server
        Start-Sleep -Milliseconds 500
        
    } catch {
        Write-Host " ✗ Failed" -ForegroundColor Red
        Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor Gray
        $failedCount++
    }
}

$elapsed = (Get-Date) - $startTime
$elapsedMin = [math]::Round($elapsed.TotalMinutes, 1)

# Final status
Write-Host "`n" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host " Processing Complete!" -ForegroundColor Green
Write-Host "================================================`n" -ForegroundColor Cyan

Write-Host "Results:" -ForegroundColor Cyan
Write-Host "  ✓ Processed: $processedCount files" -ForegroundColor Green
if ($failedCount -gt 0) {
    Write-Host "  ✗ Failed: $failedCount files" -ForegroundColor Red
}
Write-Host "  ⏱ Time taken: $elapsedMin minutes`n" -ForegroundColor Gray

# Check new KB status
Write-Host "Checking updated knowledge base status..." -ForegroundColor Yellow
try {
    $newStats = Invoke-RestMethod -Uri "$BASE_URL/api/medical/knowledge/statistics" -ErrorAction Stop
    Write-Host "`n  📊 Updated Status:" -ForegroundColor Cyan
    Write-Host "     - Documents indexed: $($newStats.total_documents)" -ForegroundColor White
    Write-Host "     - Total chunks: $($newStats.total_chunks)" -ForegroundColor White
    Write-Host "     - Knowledge level: $($newStats.knowledge_level)" -ForegroundColor White
    Write-Host "     - Model loaded: $($newStats.model_loaded)" -ForegroundColor White
    Write-Host "     - Search mode: $($newStats.search_mode)" -ForegroundColor White
} catch {
    Write-Host "  ⚠ Could not get updated KB stats" -ForegroundColor Yellow
}

Write-Host "`n✨ Knowledge base is now ready for queries!`n" -ForegroundColor Green
Write-Host "Test it in the frontend: http://127.0.0.1:5173" -ForegroundColor Cyan
Write-Host "Or test the search endpoint:" -ForegroundColor Cyan
Write-Host '  curl -X POST http://127.0.0.1:8000/api/medical/knowledge/search \' -ForegroundColor Gray
Write-Host '    -H "Content-Type: application/json" \' -ForegroundColor Gray
Write-Host '    -d ''{"query": "What is fever?", "top_k": 3}''' -ForegroundColor Gray
Write-Host "`n" -ForegroundColor White
