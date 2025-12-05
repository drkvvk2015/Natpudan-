# Test script to verify chunking fix
Write-Host "`n🧪 Testing Knowledge Base Chunking Fix..." -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Gray

# Step 1: Login
Write-Host "`n1️⃣  Logging in..." -ForegroundColor Cyan
try {
    $loginResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/auth/login" `
        -Method POST `
        -Body '{"email":"fixed@test.com","password":"test123"}' `
        -ContentType 'application/json' `
        -TimeoutSec 5
    $token = $loginResponse.access_token
    Write-Host "   [OK] Logged in as: $($loginResponse.user.email)" -ForegroundColor Green
} catch {
    Write-Host "   [ERROR] Login failed: $_" -ForegroundColor Red
    exit 1
}

# Step 2: Check current stats
Write-Host "`n2️⃣  Checking current statistics..." -ForegroundColor Cyan
try {
    $statsBefore = Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/medical/knowledge/statistics" -TimeoutSec 5
    Write-Host "   [BOX] Chunks BEFORE: $($statsBefore.total_chunks)" -ForegroundColor White
    Write-Host "   [PAGE] Documents: $($statsBefore.total_documents)" -ForegroundColor White
    Write-Host "   [SEARCH] FAISS Docs: $($statsBefore.local_faiss_documents)" -ForegroundColor White
} catch {
    Write-Host "   [ERROR] Stats check failed: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Upload a test PDF
Write-Host "`n3️⃣  Uploading test PDF..." -ForegroundColor Cyan
$testFile = "D:\Users\CNSHO\Documents\GitHub\Natpudan-\backend\data\medical_books\pediatric drug doses ( PDFDrive ).pdf"

if (-not (Test-Path $testFile)) {
    Write-Host "   [ERROR] Test file not found: $testFile" -ForegroundColor Red
    exit 1
}

try {
    Write-Host "   📤 File: $(Split-Path $testFile -Leaf)" -ForegroundColor White
    Write-Host "   [WAIT] Uploading (this may take 30-60 seconds)..." -ForegroundColor Yellow
    
    $fileContent = [System.IO.File]::ReadAllBytes($testFile)
    $fileName = Split-Path $testFile -Leaf
    
    Add-Type -AssemblyName System.Net.Http
    $httpClient = New-Object System.Net.Http.HttpClient
    $httpClient.Timeout = [TimeSpan]::FromMinutes(2)
    $httpClient.DefaultRequestHeaders.Add("Authorization", "Bearer $token")
    
    $content = New-Object System.Net.Http.MultipartFormDataContent
    $fileContent = New-Object System.Net.Http.ByteArrayContent($fileContent)
    $fileContent.Headers.ContentType = [System.Net.Http.Headers.MediaTypeHeaderValue]::Parse("application/pdf")
    $content.Add($fileContent, "files", $fileName)
    
    $response = $httpClient.PostAsync("http://127.0.0.1:8001/api/medical/knowledge/upload", $content).Result
    $responseContent = $response.Content.ReadAsStringAsync().Result
    $result = $responseContent | ConvertFrom-Json
    
    Write-Host "`n   [OK] Upload Response:" -ForegroundColor Green
    $result.results | ForEach-Object {
        Write-Host "      [PAGE] File: $($_.filename)" -ForegroundColor White
        Write-Host "      ✔️  Status: $($_.status)" -ForegroundColor $(if ($_.status -eq 'success') { 'Green' } else { 'Red' })
        Write-Host "      [BOX] Chunks: $($_.chunks)" -ForegroundColor $(if ($_.chunks -gt 0) { 'Green' } else { 'Red' })
        Write-Host "      📝 Characters: $($_.characters)" -ForegroundColor White
        
        if ($_.chunks -gt 0) {
            Write-Host "`n   [PARTY] CHUNKING IS WORKING! Generated $($_.chunks) chunks!" -ForegroundColor Green
        } elseif ($_.status -eq 'success' -and $_.chunks -eq 1) {
            Write-Host "`n   ℹ️  File uploaded as single document (full_content mode)" -ForegroundColor Cyan
        } else {
            Write-Host "`n   [WARNING]  No chunks generated" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "   [ERROR] Upload failed: $_" -ForegroundColor Red
    Write-Host "   Details: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 4: Check updated stats
Write-Host "`n4️⃣  Checking updated statistics..." -ForegroundColor Cyan
Start-Sleep -Seconds 3  # Wait for processing

try {
    $statsAfter = Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/medical/knowledge/statistics" -TimeoutSec 5
    Write-Host "   [BOX] Chunks AFTER: $($statsAfter.total_chunks)" -ForegroundColor $(if ($statsAfter.total_chunks -gt $statsBefore.total_chunks) { 'Green' } else { 'Yellow' })
    Write-Host "   [PAGE] Documents: $($statsAfter.total_documents)" -ForegroundColor White
    Write-Host "   [SEARCH] FAISS Docs: $($statsAfter.local_faiss_documents)" -ForegroundColor White
    Write-Host "   🎓 Knowledge Level: $($statsAfter.knowledge_level)" -ForegroundColor White
    
    $chunkDiff = $statsAfter.total_chunks - $statsBefore.total_chunks
    if ($chunkDiff -gt 0) {
        Write-Host "`n   [CHART] +$chunkDiff new chunks created!" -ForegroundColor Green
        Write-Host "`n[PARTY] SUCCESS! The chunking fix is working!" -ForegroundColor Green
    } else {
        Write-Host "`n   [WARNING]  No new chunks detected" -ForegroundColor Yellow
        Write-Host "   This may mean documents are stored without chunking" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   [ERROR] Stats check failed: $_" -ForegroundColor Red
}

Write-Host "`n" + ("=" * 60) -ForegroundColor Gray
Write-Host "[OK] Test Complete!" -ForegroundColor Green
