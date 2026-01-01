# Register a new user for PDF upload
param(
    [string]$BackendUrl = "http://127.0.0.1:8001"
)

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "              USER REGISTRATION" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Get user details
$fullName = Read-Host "Enter your full name"
$email = Read-Host "Enter your email"
$password = Read-Host "Enter your password" -AsSecureString
$passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)
)

Write-Host ""
Write-Host "Registering user..." -ForegroundColor Yellow

try {
    $registerResponse = Invoke-RestMethod -Uri "$BackendUrl/api/auth/register" `
        -Method POST `
        -ContentType "application/json" `
        -Body (@{
            full_name = $fullName
            email = $email
            password = $passwordPlain
            role = "doctor"
        } | ConvertTo-Json)
    
    Write-Host "[SUCCESS] User registered successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Account details:" -ForegroundColor Cyan
    Write-Host "  Name: $fullName" -ForegroundColor White
    Write-Host "  Email: $email" -ForegroundColor White
    Write-Host "  Role: doctor" -ForegroundColor White
    Write-Host ""
    Write-Host "You can now use this account to:" -ForegroundColor Yellow
    Write-Host "  1. Upload PDFs with: .\upload-large-pdfs.ps1" -ForegroundColor Cyan
    Write-Host "  2. Login to the web app: http://localhost:5173" -ForegroundColor Cyan
}
catch {
    Write-Host "[ERROR] Registration failed: $($_.Exception.Message)" -ForegroundColor Red
    
    # Check if it's a "user already exists" error
    if ($_.Exception.Message -like "*409*" -or $_.Exception.Message -like "*already exists*") {
        Write-Host ""
        Write-Host "This email is already registered." -ForegroundColor Yellow
        Write-Host "You can login with: .\upload-large-pdfs.ps1" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
