# Upload PDFs to LOCAL Knowledge Base (No API costs!)
# Uses sentence-transformers for 100% local embeddings

Write-Host "📚 LOCAL Knowledge Base Upload Script" -ForegroundColor Cyan
Write-Host "✅ No OpenAI API costs - 100% local processing" -ForegroundColor Green
Write-Host ""

# Get token first
Write-Host "🔐 Logging in..." -ForegroundColor Yellow
$loginBody = @{
    email = "doctor@example.com"
    password = "doctor123"
} | ConvertTo-Json

try {
    $authResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    $token = $authResponse.access_token
    Write-Host "✅ Logged in as: $($authResponse.user.email)" -ForegroundColor Green
} catch {
    Write-Host "❌ Login failed: $_" -ForegroundColor Red
    exit 1
}

# Headers for authenticated requests
$headers = @{
    "Authorization" = "Bearer $token"
}

# Find PDFs
Write-Host "`n🔍 Searching for PDF files..." -ForegroundColor Yellow
$pdfFiles = Get-ChildItem -Path ".\data" -Filter "*.pdf" -Recurse -ErrorAction SilentlyContinue

if ($pdfFiles.Count -eq 0) {
    Write-Host "❌ No PDF files found in .\data\" -ForegroundColor Red
    exit 1
}

Write-Host "Found $($pdfFiles.Count) PDF file(s):" -ForegroundColor Green
$pdfFiles | ForEach-Object { 
    $sizeMB = [math]::Round($_.Length/1MB, 2)
    Write-Host "  📄 $($_.Name) ($sizeMB MB)" -ForegroundColor Cyan
}

# Upload each PDF to LOCAL knowledge base
Write-Host "`n📤 Uploading to LOCAL knowledge base..." -ForegroundColor Yellow
Write-Host "⚡ Using sentence-transformers (NO API COSTS)" -ForegroundColor Green

$successCount = 0
$failCount = 0

foreach ($pdf in $pdfFiles) {
    Write-Host "`n📄 Processing: $($pdf.Name)" -ForegroundColor Cyan
    
    try {
        # Create form data
        $boundary = [System.Guid]::NewGuid().ToString()
        $fileBin = [System.IO.File]::ReadAllBytes($pdf.FullName)
        
        # Build multipart form data
        $bodyLines = @(
            "--$boundary",
            "Content-Disposition: form-data; name=`"file`"; filename=`"$($pdf.Name)`"",
            "Content-Type: application/pdf",
            "",
            [System.Text.Encoding]::GetEncoding("iso-8859-1").GetString($fileBin),
            "--$boundary",
            "Content-Disposition: form-data; name=`"use_local`"",
            "",
            "true",
            "--$boundary--"
        )
        
        $body = $bodyLines -join "`r`n"
        
        # Upload to LOCAL knowledge base endpoint
        Write-Host "  ⏳ Uploading and generating LOCAL embeddings..." -ForegroundColor Yellow
        $uploadHeaders = $headers.Clone()
        $uploadHeaders["Content-Type"] = "multipart/form-data; boundary=$boundary"
        
        $response = Invoke-RestMethod `
            -Uri "http://127.0.0.1:8001/api/medical/knowledge/upload-local" `
            -Method Post `
            -Headers $uploadHeaders `
            -Body ([System.Text.Encoding]::GetEncoding("iso-8859-1").GetBytes($body))
        
        Write-Host "  ✅ SUCCESS: $($response.message)" -ForegroundColor Green
        Write-Host "     Chunks: $($response.chunks_added) | Document ID: $($response.document_id)" -ForegroundColor Cyan
        $successCount++
        
    } catch {
        Write-Host "  ❌ FAILED: $_" -ForegroundColor Red
        $failCount++
    }
    
    Start-Sleep -Seconds 1
}

# Final statistics
Write-Host "`n" + ("="*60) -ForegroundColor Yellow
Write-Host "📊 Upload Summary:" -ForegroundColor Cyan
Write-Host "  ✅ Successful: $successCount" -ForegroundColor Green
Write-Host "  ❌ Failed: $failCount" -ForegroundColor Red

# Get updated statistics
try {
    $stats = Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/medical/knowledge/statistics" -Method Get -Headers $headers
    Write-Host "`n📊 LOCAL Knowledge Base Statistics:" -ForegroundColor Cyan
    Write-Host "  📚 Total Documents: $($stats.total_documents)" -ForegroundColor Green
    Write-Host "  📝 Total Chunks: $($stats.total_chunks)" -ForegroundColor Green
    Write-Host "  🤖 Model: $($stats.embedding_model) (LOCAL)" -ForegroundColor Yellow
    Write-Host "  💰 API Costs: $0 (100% LOCAL)" -ForegroundColor Green
} catch {
    Write-Host "`n⚠️ Could not fetch statistics" -ForegroundColor Yellow
}

Write-Host "`n✅ Upload complete!" -ForegroundColor Green
