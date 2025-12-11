# Test Medical AI Features
$ErrorActionPreference = "Continue"
$BASE_URL = "http://127.0.0.1:8000"
$TOKEN = ""

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Medical AI System Test Suite" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Test 1: Health Check
Write-Host "`n[1] Testing Health Endpoint..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$BASE_URL/health" -Method Get
    Write-Host "  ✓ Backend Status: $($health.status)" -ForegroundColor Green
    Write-Host "  ✓ Database: $($health.services.database)" -ForegroundColor Green
    Write-Host "  ✓ OpenAI: $($health.services.openai)" -ForegroundColor Green
    Write-Host "  ✓ Knowledge Base: $($health.services.knowledge_base)" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Health check failed" -ForegroundColor Red
    exit 1
}

# Test 2: User Registration/Login
Write-Host "`n[2] Testing Authentication..." -ForegroundColor Yellow
$testUser = @{
    email = "test@medical.ai"
    password = "Test123!"
    name = "Dr. Test"
    role = "doctor"
} | ConvertTo-Json

try {
    $register = Invoke-RestMethod -Uri "$BASE_URL/api/auth/register" -Method Post -Body $testUser -ContentType "application/json"
    $TOKEN = $register.access_token
    Write-Host "  ✓ User registered" -ForegroundColor Green
}
catch {
    Write-Host "  ! User exists, logging in..." -ForegroundColor Yellow
    $loginData = @{
        username = "test@medical.ai"
        password = "Test123!"
    } | ConvertTo-Json
    
    try {
        $login = Invoke-RestMethod -Uri "$BASE_URL/api/auth/login" -Method Post -Body $loginData -ContentType "application/json"
        $TOKEN = $login.access_token
        Write-Host "  ✓ Login successful" -ForegroundColor Green
    }
    catch {
        Write-Host "  ✗ Authentication failed" -ForegroundColor Red
        exit 1
    }
}

$headers = @{
    "Authorization" = "Bearer $TOKEN"
    "Content-Type" = "application/json"
}

# Test 3: Medical Diagnosis
Write-Host "`n[3] Testing AI Diagnosis..." -ForegroundColor Yellow
$diagnosisData = @{
    symptoms = @("fever", "cough", "fatigue")
    patient_history = "65-year-old male"
} | ConvertTo-Json

try {
    $diagnosis = Invoke-RestMethod -Uri "$BASE_URL/api/medical/diagnosis" -Method Post -Body $diagnosisData -Headers $headers
    Write-Host "  ✓ Diagnosis generated" -ForegroundColor Green
    Write-Host "  → Suggestions: $($diagnosis.suggestions.Count)" -ForegroundColor Cyan
}
catch {
    Write-Host "  ✗ Diagnosis failed" -ForegroundColor Red
}

# Test 4: Knowledge Base Search
Write-Host "`n[4] Testing Knowledge Base..." -ForegroundColor Yellow
$searchData = @{
    query = "What are the symptoms of pneumonia?"
    top_k = 5
    synthesize_answer = $true
} | ConvertTo-Json

try {
    $search = Invoke-RestMethod -Uri "$BASE_URL/api/medical/knowledge/search" -Method Post -Body $searchData -Headers $headers
    Write-Host "  ✓ Knowledge base search successful" -ForegroundColor Green
    Write-Host "  → Results: $($search.results.Count)" -ForegroundColor Cyan
}
catch {
    Write-Host "  ✗ Knowledge base search failed" -ForegroundColor Red
}

# Test 5: Chat with AI
Write-Host "`n[5] Testing AI Chat..." -ForegroundColor Yellow
$chatData = @{
    message = "What is hypertension treatment?"
} | ConvertTo-Json

try {
    $chat = Invoke-RestMethod -Uri "$BASE_URL/api/chat/message" -Method Post -Body $chatData -Headers $headers
    Write-Host "  ✓ Chat response received" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Chat failed" -ForegroundColor Red
}

# Test 6: Prescription Generation
Write-Host "`n[6] Testing Prescription..." -ForegroundColor Yellow
$prescriptionData = @{
    diagnosis = "Hypertension Stage 1"
    symptoms = @("elevated blood pressure")
} | ConvertTo-Json

try {
    $prescription = Invoke-RestMethod -Uri "$BASE_URL/api/prescription/generate" -Method Post -Body $prescriptionData -Headers $headers
    Write-Host "  ✓ Prescription generated" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Prescription generation failed" -ForegroundColor Red
}

# Test 7: Drug Interaction Check
Write-Host "`n[7] Testing Drug Interactions..." -ForegroundColor Yellow
$interactionData = @{
    medications = @("lisinopril", "aspirin")
} | ConvertTo-Json

try {
    $interactions = Invoke-RestMethod -Uri "$BASE_URL/api/prescription/check-interactions" -Method Post -Body $interactionData -Headers $headers
    Write-Host "  ✓ Interaction check completed" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Interaction check failed" -ForegroundColor Red
}

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Medical AI Test Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
