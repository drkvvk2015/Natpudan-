<#
    Test Medical AI Features (PowerShell 5.1 compatible, no try/catch)
    - Health
    - Register or Login
    - Diagnosis
    - Knowledge search
    - Chat
    - Prescription
    - Interaction check
#>

$ErrorActionPreference = 'Continue'
$BASE_URL = 'http://127.0.0.1:8000'
$TOKEN = ''

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Medical AI System Test Suite" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# 1) Health
Write-Host "`n[1] Testing Health Endpoint..." -ForegroundColor Yellow
$health = Invoke-RestMethod -Uri "$BASE_URL/health" -Method Get -ErrorAction SilentlyContinue
if ($null -eq $health) {
    Write-Host '  ✗ Health check failed' -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Backend Status: $($health.status)" -ForegroundColor Green
Write-Host "  ✓ Database: $($health.services.database)" -ForegroundColor Green
Write-Host "  ✓ OpenAI: $($health.services.openai)" -ForegroundColor Green
Write-Host "  ✓ Knowledge Base: $($health.services.knowledge_base)" -ForegroundColor Green

# 2) Auth: register or login
Write-Host "`n[2] Testing Authentication..." -ForegroundColor Yellow
$testUser = @{
    email = 'test@medical.ai'
    password = 'Test123!'
    full_name = 'Dr. Test'
    role = 'doctor'
} | ConvertTo-Json

$register = Invoke-RestMethod -Uri "$BASE_URL/api/auth/register" -Method Post -Body $testUser -ContentType 'application/json' -ErrorAction SilentlyContinue
if ($register -and $register.access_token) {
    $TOKEN = $register.access_token
    Write-Host '  ✓ User registered' -ForegroundColor Green
}

if (-not $TOKEN) {
    Write-Host '  ! Registration failed or user exists, attempting login...' -ForegroundColor Yellow
    $loginData = @{
        email = 'test@medical.ai'
        password = 'Test123!'
    } | ConvertTo-Json
    $login = Invoke-RestMethod -Uri "$BASE_URL/api/auth/login" -Method Post -Body $loginData -ContentType 'application/json' -ErrorAction SilentlyContinue
    if ($login -and $login.access_token) {
        $TOKEN = $login.access_token
        Write-Host '  ✓ Login successful' -ForegroundColor Green
    } else {
        Write-Host '  ✗ Authentication failed' -ForegroundColor Red
        exit 1
    }
}

$headers = @{
    'Authorization' = "Bearer $TOKEN"
    'Content-Type'  = 'application/json'
}

# 3) Diagnosis
Write-Host "`n[3] Testing AI Diagnosis..." -ForegroundColor Yellow
$diagnosisData = @{
    symptoms = @('fever', 'cough', 'fatigue')
    patient_history = '65-year-old male'
} | ConvertTo-Json

$diagnosis = Invoke-RestMethod -Uri "$BASE_URL/api/medical/diagnosis" -Method Post -Body $diagnosisData -Headers $headers -ErrorAction SilentlyContinue
if ($diagnosis) {
    Write-Host '  ✓ Diagnosis generated' -ForegroundColor Green
    if ($diagnosis.suggestions) { Write-Host "  → Suggestions: $($diagnosis.suggestions.Count)" -ForegroundColor Cyan }
} else {
    Write-Host '  ✗ Diagnosis failed' -ForegroundColor Red
}

# 4) Knowledge Base
Write-Host "`n[4] Testing Knowledge Base..." -ForegroundColor Yellow
$searchData = @{
    query = 'What are the symptoms of pneumonia?'
    top_k = 5
    synthesize_answer = $true
} | ConvertTo-Json

$search = Invoke-RestMethod -Uri "$BASE_URL/api/medical/knowledge/search" -Method Post -Body $searchData -Headers $headers -ErrorAction SilentlyContinue
if ($search) {
    Write-Host '  ✓ Knowledge base search successful' -ForegroundColor Green
    if ($search.results) { Write-Host "  → Results: $($search.results.Count)" -ForegroundColor Cyan }
} else {
    Write-Host '  ✗ Knowledge base search failed' -ForegroundColor Red
}

# 5) Chat
Write-Host "`n[5] Testing AI Chat..." -ForegroundColor Yellow
$chatData = @{ message = 'What is hypertension treatment?' } | ConvertTo-Json
$chat = Invoke-RestMethod -Uri "$BASE_URL/api/chat/message" -Method Post -Body $chatData -Headers $headers -ErrorAction SilentlyContinue
if ($chat) { Write-Host '  ✓ Chat response received' -ForegroundColor Green } else { Write-Host '  ✗ Chat failed' -ForegroundColor Red }

# 6) Prescription
Write-Host "`n[6] Testing Prescription..." -ForegroundColor Yellow
$prescriptionData = @{
    diagnosis = 'Hypertension Stage 1'
    symptoms  = @('elevated blood pressure')
} | ConvertTo-Json

$prescription = Invoke-RestMethod -Uri "$BASE_URL/api/prescription/generate-plan" -Method Post -Body $prescriptionData -Headers $headers -ErrorAction SilentlyContinue
if ($prescription) { Write-Host '  ✓ Prescription generated' -ForegroundColor Green } else { Write-Host '  ✗ Prescription generation failed' -ForegroundColor Red }

# 7) Interaction Check
Write-Host "`n[7] Testing Drug Interactions..." -ForegroundColor Yellow
$interactionData = @{ medications = @('lisinopril', 'aspirin') } | ConvertTo-Json
$interactions = Invoke-RestMethod -Uri "$BASE_URL/api/prescription/check-interactions" -Method Post -Body $interactionData -Headers $headers -ErrorAction SilentlyContinue
if ($interactions) { Write-Host '  ✓ Interaction check completed' -ForegroundColor Green } else { Write-Host '  ✗ Interaction check failed' -ForegroundColor Red }

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host 'Medical AI Test Complete!' -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
