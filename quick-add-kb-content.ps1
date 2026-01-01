# Quick Add Knowledge Base Content - Fixed version

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Adding Basic Medical Knowledge" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$BASE_URL = "http://127.0.0.1:8000"

# Check backend
try {
    $health = Invoke-RestMethod -Uri "$BASE_URL/health" -ErrorAction Stop
    Write-Host "[✓] Backend is $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "[✗] Backend is offline. Start it first!" -ForegroundColor Red
    exit 1
}

# Login as admin
Write-Host "`n[1/3] Logging in as admin..." -ForegroundColor Yellow
$loginBody = @{
    email = "admin@admin.com"
    password = "admin123"
} | ConvertTo-Json

try {
    $login = Invoke-RestMethod -Uri "$BASE_URL/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json" -ErrorAction Stop
    $TOKEN = $login.access_token
    Write-Host "  ✓ Logged in successfully" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Create medical content
Write-Host "`n[2/3] Creating medical content..." -ForegroundColor Yellow

$medicalContent = @"
# Basic Medical Reference Guide

## Fever (Pyrexia)

**Definition:**
Fever is an elevation of body temperature above the normal range, typically defined as a core temperature of 38.0°C (100.4°F) or higher.

**Clinical Presentation:**
- Body temperature ≥38.0°C (100.4°F) oral or ≥38.3°C (101°F) rectal
- Chills and rigors during temperature rise
- Diaphoresis during temperature decline
- Headache, malaise, myalgias (body aches)
- Tachycardia (increased heart rate)

**Classification:**
- Low-grade: 38.0-38.9°C (100.4-102°F)
- Moderate: 39.0-40.0°C (102.2-104°F)
- High-grade: >40.0°C (>104°F)

**Common Causes:**
- Infections (viral, bacterial, fungal, parasitic)
- Inflammatory conditions (rheumatoid arthritis, inflammatory bowel disease)
- Malignancies (lymphoma, leukemia)
- Drug reactions
- Autoimmune diseases

**Treatment:**
**Antipyretics:**
- Acetaminophen (Tylenol): 325-1000mg PO q4-6h (max 4g/day)
- Ibuprofen (Advil, Motrin): 200-400mg PO q4-6h (max 3200mg/day)
- Aspirin: 325-650mg PO q4-6h (avoid in children - Reye's syndrome risk)

**Supportive Care:**
- Adequate hydration (oral or IV fluids)
- Rest and light clothing
- Tepid sponge baths

---

## Hypertension

**Definition:**
Hypertension (high blood pressure) is persistently elevated arterial blood pressure, defined as systolic BP ≥130 mmHg or diastolic BP ≥80 mmHg (per 2017 ACC/AHA guidelines).

**Classification:**
- Normal: <120/80 mmHg
- Elevated: 120-129/<80 mmHg
- Stage 1: 130-139/80-89 mmHg
- Stage 2: ≥140/90 mmHg
- Hypertensive Crisis: >180/120 mmHg

**Treatment:**
**Lifestyle Modifications:**
- DASH diet (low sodium, high potassium)
- Weight loss (5-10% reduces BP significantly)
- Regular aerobic exercise (30 min/day, 5 days/week)
- Limit alcohol
- Smoking cessation

**Pharmacotherapy - First-line agents:**
- ACE inhibitors: Lisinopril 10-40mg daily, Enalapril 5-40mg daily
- ARBs: Losartan 50-100mg daily, Valsartan 80-320mg daily
- Calcium channel blockers: Amlodipine 5-10mg daily
- Thiazide diuretics: Hydrochlorothiazide 12.5-25mg daily

**Target BP:**
- General population: <130/80 mmHg
- Diabetes/CKD: <130/80 mmHg

---

## Pneumonia

**Definition:**
Pneumonia is an acute infection of the pulmonary parenchyma, characterized by inflammation of the alveoli and surrounding lung tissue.

**Clinical Presentation:**
- Fever, chills, rigors
- Productive cough (purulent sputum)
- Pleuritic chest pain
- Dyspnea (shortness of breath)
- Tachypnea, tachycardia
- Crackles/rales on auscultation

**Diagnosis:**
- Chest X-ray: infiltrates, consolidation
- CBC: leukocytosis
- Sputum culture and Gram stain
- Blood cultures (if severe)

**Treatment - Community-Acquired Pneumonia:**
**Outpatient (no comorbidities):**
- Amoxicillin 1g TID or
- Doxycycline 100mg BID or
- Macrolide (Azithromycin 500mg day 1, then 250mg days 2-5)

**Duration:** Typically 5-7 days for uncomplicated CAP

**Supportive Care:**
- Oxygen therapy (maintain SpO2 >92%)
- IV fluids for hydration
- Antipyretics for fever

---

**ICD-10 Codes:**
- R50.9: Fever, unspecified
- I10: Essential (primary) hypertension
- J18.9: Pneumonia, unspecified organism

**Last Updated:** December 2025
"@

Write-Host "  ✓ Medical content created" -ForegroundColor Green

# Save to temp file
Write-Host "`n[3/3] Uploading to knowledge base..." -ForegroundColor Yellow

$tempFile = [System.IO.Path]::GetTempFileName()
$txtFile = $tempFile.Replace(".tmp", ".txt")
Move-Item $tempFile $txtFile -Force
Set-Content -Path $txtFile -Value $medicalContent -Encoding UTF8

try {
    # PowerShell multipart upload
    $boundary = [System.Guid]::NewGuid().ToString()
    $LF = "`r`n"
    
    $fileBytes = [System.IO.File]::ReadAllBytes($txtFile)
    $fileContent = [System.Text.Encoding]::GetEncoding('iso-8859-1').GetString($fileBytes)
    
    $bodyLines = (
        "--$boundary",
        "Content-Disposition: form-data; name=`"file`"; filename=`"Basic_Medical_Reference.txt`"",
        "Content-Type: text/plain",
        "",
        $fileContent,
        "--$boundary--"
    ) -join $LF
    
    $headers = @{
        "Authorization" = "Bearer $TOKEN"
        "Content-Type" = "multipart/form-data; boundary=$boundary"
    }
    
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/medical/knowledge/upload" `
        -Method Post `
        -Headers $headers `
        -Body $bodyLines `
        -TimeoutSec 60 `
        -ErrorAction Stop
    
    Write-Host "  ✓ Upload successful!" -ForegroundColor Green
    Write-Host "  Status: $($response.status)" -ForegroundColor Gray
    
    # Wait for processing
    Write-Host "`n  ⏳ Processing document (creating embeddings)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Verify
    $stats = Invoke-RestMethod -Uri "$BASE_URL/api/medical/knowledge/statistics"
    Write-Host "  ✓ Documents: $($stats.total_documents)" -ForegroundColor Green
    Write-Host "  ✓ Chunks: $($stats.total_chunks)" -ForegroundColor Green
    
} catch {
    Write-Host "  ✗ Upload failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  Error details: $($_.ErrorDetails.Message)" -ForegroundColor Gray
} finally {
    Remove-Item $txtFile -ErrorAction SilentlyContinue
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Done!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Clear browser cache (Ctrl+Shift+Delete)" -ForegroundColor White
Write-Host "  2. Go to: http://127.0.0.1:5173" -ForegroundColor White
Write-Host "  3. Login: admin@admin.com / admin123" -ForegroundColor White
Write-Host "  4. KB indicator should show documents!`n" -ForegroundColor White
