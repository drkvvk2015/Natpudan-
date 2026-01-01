# Initialize Knowledge Base - Process all medical PDFs and create FAISS index
# This script uploads PDFs to the knowledge base API for processing

$backendUrl = "http://127.0.0.1:8001"
$uploadEndpoint = "$backendUrl/api/medical/knowledge/upload"
$statsEndpoint = "$backendUrl/api/medical/knowledge/statistics"

Write-Host "🏥 NATPUDAN KNOWLEDGE BASE INITIALIZATION" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Get all PDF files from medical_books directory
$pdfDir = "D:\Users\CNSHO\Documents\GitHub\Natpudan-\backend\data\medical_books"
$pdfFiles = Get-ChildItem -Path $pdfDir -Filter "*.pdf" -File | Sort-Object Length

Write-Host "`n📚 Found $($pdfFiles.Count) PDF files" -ForegroundColor Yellow
$totalSize = ($pdfFiles | Measure-Object -Property Length -Sum).Sum / 1GB
Write-Host "📊 Total size: $([math]::Round($totalSize, 2)) GB" -ForegroundColor Yellow

# Check backend health
Write-Host "`n🔍 Checking backend status..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "$backendUrl/health" -TimeoutSec 5
    Write-Host "✅ Backend is healthy (uptime: $($health.uptime_seconds)s)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend is not responding! Please start the backend first." -ForegroundColor Red
    Write-Host "   Run: .\start-backend.ps1" -ForegroundColor Yellow
    exit 1
}

# Login to get authentication token
Write-Host "`n🔐 Logging in..." -ForegroundColor Cyan
$loginBody = @{
    email = "fixed@test.com"
    password = "test123"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$backendUrl/api/auth/login" `
        -Method POST `
        -Body $loginBody `
        -ContentType "application/json" `
        -TimeoutSec 10
    
    $token = $loginResponse.access_token
    Write-Host "✅ Logged in as: $($loginResponse.user.email)" -ForegroundColor Green
} catch {
    Write-Host "❌ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Make sure you have a valid user account" -ForegroundColor Yellow
    exit 1
}

# Function to refresh token if needed
function Get-FreshToken {
    try {
        $loginBody = @{
            email = "fixed@test.com"
            password = "test123"
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$backendUrl/api/auth/login" `
            -Method POST `
            -Body $loginBody `
            -ContentType "application/json" `
            -TimeoutSec 10
        
        return $response.access_token
    } catch {
        Write-Host "⚠️ Token refresh failed: $($_.Exception.Message)" -ForegroundColor Yellow
        return $null
    }
}

# Get current stats
Write-Host "`n📊 Current knowledge base statistics:" -ForegroundColor Cyan
try {
    $preStats = Invoke-RestMethod -Uri $statsEndpoint -Method GET
    Write-Host "  Documents: $($preStats.total_documents)" -ForegroundColor White
    Write-Host "  Chunks: $($preStats.total_chunks)" -ForegroundColor White
    Write-Host "  Uploaded Files: $($preStats.uploaded_files)" -ForegroundColor White
} catch {
    Write-Host "⚠️ Could not fetch statistics: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n🚀 Starting upload process..." -ForegroundColor Green
Write-Host "⏱️ This will take 30-60 minutes for large PDFs" -ForegroundColor Yellow
Write-Host ""

$successCount = 0
$failCount = 0
$startTime = Get-Date

foreach ($pdf in $pdfFiles) {
    $fileNum = $pdfFiles.IndexOf($pdf) + 1
    $sizeMB = [math]::Round($pdf.Length / 1MB, 2)
    
    Write-Host "[$fileNum/$($pdfFiles.Count)] Processing: $($pdf.Name) ($sizeMB MB)" -ForegroundColor Cyan

    try {
        # Use Python for reliable multipart upload with authentication
        $pythonScript = @"
import requests
import sys

file_path = r'$($pdf.FullName)'
token = '$token'

try:
    with open(file_path, 'rb') as f:
        files = {'files': ('$($pdf.Name)', f, 'application/pdf')}
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.post(
            '$uploadEndpoint',
            files=files,
            headers=headers,
            timeout=300
        )
    
    result = response.json()
    for r in result.get('results', []):
        print(f"Status: {r.get('status')}")
        print(f"Chunks: {r.get('chunks', 0)}")
        print(f"Characters: {r.get('characters', 0)}")
        
        if r.get('status') == 'success':
            sys.exit(0)
    
    # Check if 401 Unauthorized - token expired
    if response.status_code == 401:
        print('TOKEN_EXPIRED')
        sys.exit(2)
    
    sys.exit(1)
        
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
"@
        
        $result = & "D:\Users\CNSHO\Documents\GitHub\Natpudan-\.venv311\Scripts\python.exe" -c $pythonScript
        
        if ($LASTEXITCODE -eq 0) {
            # Success
            Write-Host "  ✅ Success!" -ForegroundColor Green
            $successCount++
        } elseif ($LASTEXITCODE -eq 2) {
            # Token expired - refresh and retry
            Write-Host "  🔄 Token expired, refreshing..." -ForegroundColor Yellow
            $token = Get-FreshToken
            
            if ($token) {
                Write-Host "  🔄 Retrying upload..." -ForegroundColor Cyan
                # Retry with new token
                $pythonScript = $pythonScript -replace "token = '.*'", "token = '$token'"
                $result = & "D:\Users\CNSHO\Documents\GitHub\Natpudan-\.venv311\Scripts\python.exe" -c $pythonScript
                
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "  ✅ Success after retry!" -ForegroundColor Green
                    $successCount++
                } else {
                    Write-Host "  ❌ Failed after retry" -ForegroundColor Red
                    $failCount++
                }
            } else {
                Write-Host "  ❌ Token refresh failed" -ForegroundColor Red
                $failCount++
            }
        } else {
            Write-Host "  ❌ Failed: $result" -ForegroundColor Red
            $failCount++
        }
        
    } catch {
        Write-Host "  ❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
        $failCount++
    }

    # Progress summary every 5 files
    if ($fileNum % 5 -eq 0) {
        $elapsed = (Get-Date) - $startTime
        $avgTimePerFile = $elapsed.TotalSeconds / $fileNum
        $remainingFiles = $pdfFiles.Count - $fileNum
        $estimatedRemaining = [math]::Round($avgTimePerFile * $remainingFiles / 60, 1)
        
        Write-Host ""
        Write-Host "  📈 Progress: $fileNum/$($pdfFiles.Count) ($successCount success, $failCount failed)" -ForegroundColor Yellow
        Write-Host "  ⏱️ Estimated time remaining: $estimatedRemaining minutes" -ForegroundColor Yellow
        Write-Host ""
    }

    # Small delay between uploads to prevent overload
    Start-Sleep -Milliseconds 200
}

$totalTime = ((Get-Date) - $startTime).TotalMinutes

Write-Host "`n✨ UPLOAD PROCESS COMPLETED!" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green
Write-Host "✅ Successful: $successCount" -ForegroundColor Green
Write-Host "❌ Failed: $failCount" -ForegroundColor Red
Write-Host "⏱️ Total time: $([math]::Round($totalTime, 1)) minutes" -ForegroundColor Yellow

# Get final stats
Write-Host "`n📊 Final knowledge base statistics:" -ForegroundColor Cyan
try {
    $postStats = Invoke-RestMethod -Uri $statsEndpoint -Method GET
    Write-Host "  Documents: $($postStats.total_documents)" -ForegroundColor White
    Write-Host "  Chunks: $($postStats.total_chunks)" -ForegroundColor White
    Write-Host "  Uploaded Files: $($postStats.uploaded_files)" -ForegroundColor White
    Write-Host "  Model: $($postStats.embedding_model)" -ForegroundColor White
    Write-Host "  Size: $($postStats.total_upload_size_mb) MB" -ForegroundColor White
} catch {
    Write-Host "⚠️ Could not fetch final statistics" -ForegroundColor Yellow
}

Write-Host "`n🎉 Knowledge base is ready to use!" -ForegroundColor Green
Write-Host "   Open http://localhost:5173 and navigate to Knowledge Base" -ForegroundColor Cyan
