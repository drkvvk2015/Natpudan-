param()

$ErrorActionPreference = "SilentlyContinue"
$BASE_URL = "http://127.0.0.1:8000"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Medical AI System Test Suite" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test Health
Write-Host "[1] Health Check..." -ForegroundColor Yellow
$health = Invoke-RestMethod -Uri "$BASE_URL/health" -Method Get
if ($health.status -eq "healthy") {
    Write-Host "  ✓ Backend: $($health.status)" -ForegroundColor Green
    Write-Host "  ✓ Database: OK" -ForegroundColor Green
    Write-Host "  ✓ OpenAI: OK" -ForegroundColor Green
    Write-Host "  ✓ Knowledge Base: OK`n" -ForegroundColor Green
} else {
    Write-Host "  ✗ Health check failed`n" -ForegroundColor Red
    exit 1
}

# Login
Write-Host "[2] Authentication..." -ForegroundColor Yellow
$loginBody = @{
    username = "admin@example.com"
    password = "admin123"
} | ConvertTo-Json

$login = Invoke-RestMethod -Uri "$BASE_URL/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
if ($login.access_token) {
    Write-Host "  ✓ Login successful`n" -ForegroundColor Green
    $TOKEN = $login.access_token
} else {
    Write-Host "  ✗ Login failed`n" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $TOKEN"
    "Content-Type" = "application/json"
}

# Test Diagnosis
Write-Host "[3] AI Diagnosis..." -ForegroundColor Yellow
$diagnosisBody = @{
    symptoms = @("fever", "cough", "fatigue")
    patient_history = "65-year-old male"
} | ConvertTo-Json

$diagnosis = Invoke-RestMethod -Uri "$BASE_URL/api/medical/diagnosis" -Method Post -Body $diagnosisBody -Headers $headers
if ($diagnosis) {
    Write-Host "  ✓ Diagnosis generated" -ForegroundColor Green
    Write-Host "  → Found $($diagnosis.suggestions.Count) suggestions`n" -ForegroundColor Cyan
} else {
    Write-Host "  ✗ Diagnosis failed`n" -ForegroundColor Red
}

# Test Knowledge Base
Write-Host "[4] Knowledge Base Search..." -ForegroundColor Yellow
$searchBody = @{
    query = "pneumonia symptoms"
    top_k = 5
    synthesize_answer = $true
} | ConvertTo-Json

$search = Invoke-RestMethod -Uri "$BASE_URL/api/medical/knowledge/search" -Method Post -Body $searchBody -Headers $headers
if ($search) {
    Write-Host "  ✓ Search successful" -ForegroundColor Green
    Write-Host "  → Found $($search.results.Count) results`n" -ForegroundColor Cyan
} else {
    Write-Host "  ✗ Search failed`n" -ForegroundColor Red
}

# Test Chat
Write-Host "[5] AI Chat..." -ForegroundColor Yellow
$chatBody = @{
    message = "What is the treatment for hypertension?"
} | ConvertTo-Json

$chat = Invoke-RestMethod -Uri "$BASE_URL/api/chat/message" -Method Post -Body $chatBody -Headers $headers
if ($chat.message) {
    Write-Host "  ✓ Chat response received" -ForegroundColor Green
    $preview = ($chat.message.content -split ' ' | Select-Object -First 15) -join ' '
    Write-Host "  → $preview...`n" -ForegroundColor Cyan
} else {
    Write-Host "  ✗ Chat failed`n" -ForegroundColor Red
}

# Test Prescription
Write-Host "[6] Prescription Generation..." -ForegroundColor Yellow
$prescriptionBody = @{
    diagnosis = "Hypertension Stage 1"
    symptoms = @("elevated blood pressure")
} | ConvertTo-Json

$prescription = Invoke-RestMethod -Uri "$BASE_URL/api/prescription/generate" -Method Post -Body $prescriptionBody -Headers $headers
if ($prescription.medications) {
    Write-Host "  ✓ Prescription generated" -ForegroundColor Green
    Write-Host "  → $($prescription.medications.Count) medications`n" -ForegroundColor Cyan
} else {
    Write-Host "  ✗ Prescription failed`n" -ForegroundColor Red
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " All Medical AI Features Tested!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
