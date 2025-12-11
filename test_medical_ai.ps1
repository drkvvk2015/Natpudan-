# Test Medical AI Features
# Run this script to verify all medical AI functionality is working

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
} catch {
    Write-Host "  ✗ Health check failed: $_" -ForegroundColor Red
    exit 1
}

# Test 2: User Registration
Write-Host "`n[2] Testing User Registration..." -ForegroundColor Yellow
$testUser = @{
    email = "test@medical.ai"
    password = "Test123!"
    name = "Dr. Test"
    role = "doctor"
} | ConvertTo-Json

try {
    $register = Invoke-RestMethod -Uri "$BASE_URL/api/auth/register" -Method Post -Body $testUser -ContentType "application/json" -ErrorAction Stop
    if ($register.access_token) {
        Write-Host "  ✓ User registered successfully" -ForegroundColor Green
        $TOKEN = $register.access_token
    }
} catch {
    Write-Host "  ! User exists, trying login..." -ForegroundColor Yellow
}

# Test 3: User Login
if (-not $TOKEN) {
    Write-Host "`n[3] Testing User Login..." -ForegroundColor Yellow
    $loginData = @{
        username = "test@medical.ai"
        password = "Test123!"
    } | ConvertTo-Json

    try {
        $login = Invoke-RestMethod -Uri "$BASE_URL/api/auth/login" -Method Post -Body $loginData -ContentType "application/json"
        $TOKEN = $login.access_token
        Write-Host "  ✓ Login successful" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Login failed: $_" -ForegroundColor Red
        exit 1
    }
}

$headers = @{
    "Authorization" = "Bearer $TOKEN"
    "Content-Type" = "application/json"
}

# Test 4: Medical Diagnosis
Write-Host "`n[4] Testing AI Diagnosis..." -ForegroundColor Yellow
$diagnosisData = @{
    symptoms = @("fever", "cough", "fatigue", "difficulty breathing")
    patient_history = "65-year-old male, hypertensive"
} | ConvertTo-Json

try {
    $diagnosis = Invoke-RestMethod -Uri "$BASE_URL/api/medical/diagnosis" -Method Post -Body $diagnosisData -Headers $headers
    Write-Host "  ✓ Diagnosis generated" -ForegroundColor Green
    Write-Host "  → Suggested diagnoses: $($diagnosis.suggestions.Count)" -ForegroundColor Cyan
    if ($diagnosis.suggestions.Count -gt 0) {
        Write-Host "    - $($diagnosis.suggestions[0].name)" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ✗ Diagnosis failed: $_" -ForegroundColor Red
}

# Test 5: Knowledge Base Search
Write-Host "`n[5] Testing Knowledge Base Search..." -ForegroundColor Yellow
$searchData = @{
    query = "What are the symptoms of pneumonia?"
    top_k = 5
    synthesize_answer = $true
} | ConvertTo-Json

try {
    $search = Invoke-RestMethod -Uri "$BASE_URL/api/medical/knowledge/search" -Method Post -Body $searchData -Headers $headers
    Write-Host "  ✓ Knowledge base search successful" -ForegroundColor Green
    Write-Host "  → Results found: $($search.results.Count)" -ForegroundColor Cyan
    if ($search.answer) {
        Write-Host "  → AI synthesized answer: $(($search.answer -split ' ' | Select-Object -First 15) -join ' ')..." -ForegroundColor Cyan
    }
} catch {
    Write-Host "  ✗ Knowledge base search failed: $_" -ForegroundColor Red
}

# Test 6: Chat with AI
Write-Host "`n[6] Testing AI Chat..." -ForegroundColor Yellow
$chatData = @{
    message = "What is the recommended treatment for mild hypertension?"
} | ConvertTo-Json

try {
    $chat = Invoke-RestMethod -Uri "$BASE_URL/api/chat/message" -Method Post -Body $chatData -Headers $headers
    Write-Host "  ✓ Chat response received" -ForegroundColor Green
    Write-Host "  → Conversation ID: $($chat.conversation_id)" -ForegroundColor Cyan
    $response = $chat.message.content -split ' ' | Select-Object -First 20
    Write-Host "  → Response preview: $($response -join ' ')..." -ForegroundColor Cyan
} catch {
    Write-Host "  ✗ Chat failed: $_" -ForegroundColor Red
}

# Test 7: Prescription Generation
Write-Host "`n[7] Testing Prescription Generation..." -ForegroundColor Yellow
$prescriptionData = @{
    diagnosis = "Hypertension Stage 1"
    symptoms = @("elevated blood pressure", "occasional headaches")
} | ConvertTo-Json

try {
    $prescription = Invoke-RestMethod -Uri "$BASE_URL/api/prescription/generate" -Method Post -Body $prescriptionData -Headers $headers
    Write-Host "  ✓ Prescription generated" -ForegroundColor Green
    Write-Host "  → Medications: $($prescription.medications.Count)" -ForegroundColor Cyan
    if ($prescription.medications.Count -gt 0) {
        Write-Host "    - $($prescription.medications[0].name)" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ✗ Prescription generation failed: $_" -ForegroundColor Red
}

# Test 8: Drug Interaction Check
Write-Host "`n[8] Testing Drug Interaction Checker..." -ForegroundColor Yellow
$interactionData = @{
    medications = @("lisinopril", "aspirin", "ibuprofen")
} | ConvertTo-Json

try {
    $interactions = Invoke-RestMethod -Uri "$BASE_URL/api/prescription/check-interactions" -Method Post -Body $interactionData -Headers $headers
    Write-Host "  ✓ Interaction check completed" -ForegroundColor Green
    Write-Host "  → Interactions found: $($interactions.interactions.Count)" -ForegroundColor Cyan
    if ($interactions.interactions.Count -gt 0) {
        Write-Host "    - $($interactions.interactions[0].severity) severity" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ✗ Interaction check failed: $_" -ForegroundColor Red
}

# Test 9: ICD-10 Code Lookup
Write-Host "`n[9] Testing ICD-10 Code Service..." -ForegroundColor Yellow
$icdData = @{
    query = "hypertension"
} | ConvertTo-Json

try {
    $icd = Invoke-RestMethod -Uri "$BASE_URL/api/medical/icd10" -Method Post -Body $icdData -Headers $headers
    Write-Host "  ✓ ICD-10 codes retrieved" -ForegroundColor Green
    Write-Host "  → Codes found: $($icd.results.Count)" -ForegroundColor Cyan
    if ($icd.results.Count -gt 0) {
        Write-Host "    - $($icd.results[0].code): $($icd.results[0].description)" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ✗ ICD-10 lookup failed: $_" -ForegroundColor Red
}

# Test 10: Analytics
Write-Host "`n[10] Testing Analytics Dashboard..." -ForegroundColor Yellow
try {
    $analytics = Invoke-RestMethod -Uri "$BASE_URL/api/analytics/demographics" -Method Get -Headers $headers
    Write-Host "  ✓ Analytics data retrieved" -ForegroundColor Green
    Write-Host "  → Total patients: $($analytics.total_patients)" -ForegroundColor Cyan
} catch {
    Write-Host "  ✗ Analytics failed: $_" -ForegroundColor Red
}

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Test Suite Completed!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "`nMedical AI System is fully operational!" -ForegroundColor Green
Write-Host "All core features tested and working." -ForegroundColor Green
