param(
    [switch]$Confirm = $false
)

$BASE_URL = "http://localhost:8000"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Knowledge Base Reset" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check backend
try {
    $health = Invoke-RestMethod -Uri "$BASE_URL/health" -TimeoutSec 5
    Write-Host "OK - Backend is running" -ForegroundColor Green
}
catch {
    Write-Host "ERROR - Backend not available" -ForegroundColor Red
    exit 1
}

# Login as admin
Write-Host "Logging in as admin..." -ForegroundColor Yellow
$loginBody = @{
    email = "admin@admin.com"
    password = "admin123"
} | ConvertTo-Json

try {
    $login = Invoke-RestMethod -Uri "$BASE_URL/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    $TOKEN = $login.access_token
    Write-Host "OK - Admin logged in" -ForegroundColor Green
}
catch {
    Write-Host "ERROR - Login failed" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $TOKEN"
    "Content-Type" = "application/json"
}

# Confirm reset
Write-Host ""
Write-Host "This will permanently delete:" -ForegroundColor Yellow
Write-Host "  - All uploaded documents" -ForegroundColor White
Write-Host "  - All indexed medical sources" -ForegroundColor White
Write-Host "  - FAISS vector index" -ForegroundColor White
Write-Host "  - Embeddings cache" -ForegroundColor White
Write-Host ""

if (-not $Confirm) {
    $response = Read-Host "Type 'yes' to confirm reset"
    $response = $response.ToLower().Trim()
    if ($response -ne "yes" -and $response -ne "y") {
        Write-Host "Reset cancelled" -ForegroundColor Yellow
        exit 0
    }
}

# Execute reset
Write-Host ""
Write-Host "Resetting knowledge base..." -ForegroundColor Yellow

try {
    $reset = Invoke-RestMethod -Uri "$BASE_URL/api/medical/knowledge/reset" -Method Post -Headers $headers
    
    Write-Host "OK - Reset successful" -ForegroundColor Green
    Write-Host ""
    Write-Host "Cleared:" -ForegroundColor Cyan
    Write-Host "  - Database documents: $($reset.cleared.database_documents)" -ForegroundColor White
    Write-Host "  - Uploaded files: $($reset.cleared.uploaded_files)" -ForegroundColor White
    Write-Host "  - FAISS index: $($reset.cleared.faiss_index)" -ForegroundColor White
    Write-Host "  - Embeddings cache: $($reset.cleared.embeddings_cache)" -ForegroundColor White
    Write-Host ""
    Write-Host "Remaining documents: $($reset.remaining_documents)" -ForegroundColor White
}
catch {
    Write-Host "ERROR - Reset failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Knowledge Base Ready" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "All data has been cleared. Ready for fresh start!" -ForegroundColor Green
Write-Host ""
