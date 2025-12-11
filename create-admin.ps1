param(
    [string]$Email = "admin@admin.com",
    [string]$Password = "admin123"
)

$BASE_URL = "http://localhost:8000"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Creating Admin User" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    $health = Invoke-RestMethod -Uri "$BASE_URL/health" -TimeoutSec 5
    Write-Host "OK - Backend is running" -ForegroundColor Green
}
catch {
    Write-Host "ERROR - Backend not available" -ForegroundColor Red
    exit 1
}

try {
    $registerBody = @{
        email = $Email
        password = $Password
        full_name = "Administrator"
        role = "admin"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$BASE_URL/api/auth/register" -Method Post -Body $registerBody -ContentType "application/json"
    
    Write-Host "OK - Admin user created" -ForegroundColor Green
}
catch {
    $code = $_.Exception.Response.StatusCode.Value__
    if ($code -eq 400) {
        Write-Host "INFO - User already exists, checking..." -ForegroundColor Yellow
        
        $loginBody = @{
            email = $Email
            password = $Password
        } | ConvertTo-Json
        
        $login = Invoke-RestMethod -Uri "$BASE_URL/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
        Write-Host "OK - Admin user verified" -ForegroundColor Green
    }
    else {
        Write-Host "ERROR - $_" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " ADMIN CREDENTIALS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Email:    admin@admin.com" -ForegroundColor White
Write-Host "  Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "  Login:    http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
