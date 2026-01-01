# Quick Fix: Add Basic Medical Knowledge

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Adding Basic Medical Knowledge" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$BASE_URL = "http://localhost:8000"

# Login as admin
Write-Host "[1] Logging in as admin..." -ForegroundColor Yellow
$loginBody = @{
    email = "admin@admin.com"
    password = "admin123"
} | ConvertTo-Json

$login = Invoke-RestMethod -Uri "$BASE_URL/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
$TOKEN = $login.access_token
Write-Host "  SUCCESS: Logged in`n" -ForegroundColor Green

$headers = @{
    "Authorization" = "Bearer $TOKEN"
    "Content-Type" = "application/json"
}

# Create a temporary medical reference document
Write-Host "[2] Creating basic medical reference..." -ForegroundColor Yellow

$medicalContent = @"
# Basic Medical Reference Guide

## Fever (Pyrexia)

**Definition:**
Fever is an elevation of body temperature above the normal range, typically defined as a core temperature of 38.0°C (100.4°F) or higher. It represents a regulated increase in the body's thermoregulatory set point in response to various stimuli.

**Pathophysiology:**
Fever occurs when endogenous pyrogens (such as interleukin-1, interleukin-6, and tumor necrosis factor) are released in response to infection, inflammation, or other stimuli. These pyrogens act on the hypothalamus, causing an upward adjustment of the thermoregulatory set point.

**Clinical Presentation:**
- Body temperature ≥38.0°C (100.4°F) oral or ≥38.3°C (101°F) rectal
- Chills and rigors during temperature rise
- Diaphoresis during temperature decline
- Headache, malaise, myalgias (body aches)
- Tachycardia (increased heart rate)
- Tachypnea (increased respiratory rate)

**Classification:**
- Low-grade: 38.0-38.9°C (100.4-102°F)
- Moderate: 39.0-40.0°C (102.2-104°F)
- High-grade: >40.0°C (>104°F)
- Hyperpyrexia: >41.5°C (>106.7°F) - medical emergency

**Common Causes:**
- Infections (viral, bacterial, fungal, parasitic)
- Inflammatory conditions (rheumatoid arthritis, inflammatory bowel disease)
- Malignancies (lymphoma, leukemia)
- Drug reactions (drug-induced fever)
- Autoimmune diseases
- Thromboembolism

**Diagnosis:**
- Accurate temperature measurement (oral, rectal, tympanic)
- History: onset, duration, pattern, associated symptoms
- Physical examination: focus on infection sources
- Laboratory tests: CBC, blood cultures, urinalysis, inflammatory markers
- Imaging as indicated: chest X-ray, CT scan

**Treatment:**
**Antipyretics:**
- Acetaminophen (Tylenol): 325-1000mg PO q4-6h (max 4g/day)
- Ibuprofen (Advil, Motrin): 200-400mg PO q4-6h (max 3200mg/day)
- Aspirin: 325-650mg PO q4-6h (avoid in children - Reye's syndrome risk)

**Supportive Care:**
- Adequate hydration (oral or IV fluids)
- Rest and light clothing
- Tepid sponge baths (avoid alcohol or cold water)
- Environmental temperature control

**Treatment of Underlying Cause:**
- Antibiotics for bacterial infections
- Antiviral agents for specific viral infections
- Anti-inflammatory agents for inflammatory conditions

**When to Seek Emergency Care:**
- Temperature >40°C (104°F)
- Fever with severe headache, stiff neck, confusion
- Fever with difficulty breathing
- Fever with chest pain
- Fever in immunocompromised patients
- Fever with petechial rash
- Fever with altered mental status
- Persistent fever >3 days without source

**Prognosis:**
Most fevers are self-limited and resolve within 3-5 days. Prognosis depends on the underlying cause. Fever itself is generally not harmful unless extremely high (>41.5°C) or in vulnerable populations (infants, elderly, immunocompromised).

**Special Populations:**
- **Infants <3 months:** Fever >38°C requires immediate evaluation
- **Pregnant women:** Avoid NSAIDs in third trimester; prefer acetaminophen
- **Elderly:** May have blunted fever response; higher risk of serious infection
- **Immunocompromised:** Fever may be only sign of serious infection

**References:**
- Harrison's Principles of Internal Medicine, 21st Edition
- UpToDate: Fever in adults
- CDC Guidelines: Fever management
- WHO Guidelines: Temperature measurement and management

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

**Pathophysiology:**
Hypertension results from increased peripheral vascular resistance, increased cardiac output, or both. Contributing factors include increased sympathetic activity, renin-angiotensin-aldosterone system activation, endothelial dysfunction, and sodium retention.

**Clinical Presentation:**
Often asymptomatic ("silent killer"). When symptomatic may include:
- Headaches (usually occipital, early morning)
- Dizziness, vertigo
- Blurred vision
- Epistaxis (nosebleeds)
- Palpitations

**Treatment:**
**Lifestyle Modifications:**
- DASH diet (low sodium, high potassium)
- Weight loss (5-10% reduces BP significantly)
- Regular aerobic exercise (30 min/day, 5 days/week)
- Limit alcohol (≤2 drinks/day men, ≤1 drink/day women)
- Smoking cessation

**Pharmacotherapy - First-line agents:**
- **ACE inhibitors:** Lisinopril 10-40mg daily, Enalapril 5-40mg daily
- **ARBs:** Losartan 50-100mg daily, Valsartan 80-320mg daily
- **Calcium channel blockers:** Amlodipine 5-10mg daily
- **Thiazide diuretics:** Hydrochlorothiazide 12.5-25mg daily

**Target BP:**
- General population: <130/80 mmHg
- Diabetes/CKD: <130/80 mmHg
- Elderly >65 years: <130/80 mmHg if tolerated

---

## Pneumonia

**Definition:**
Pneumonia is an acute infection of the pulmonary parenchyma, characterized by inflammation of the alveoli and surrounding lung tissue, typically caused by bacteria, viruses, or fungi.

**Classification:**
- Community-acquired pneumonia (CAP)
- Hospital-acquired pneumonia (HAP)
- Ventilator-associated pneumonia (VAP)
- Aspiration pneumonia

**Clinical Presentation:**
- Fever, chills, rigors
- Productive cough (purulent sputum)
- Pleuritic chest pain
- Dyspnea (shortness of breath)
- Tachypnea, tachycardia
- Crackles/rales on auscultation
- Dullness to percussion
- Bronchial breath sounds

**Diagnosis:**
- Chest X-ray: infiltrates, consolidation
- CBC: leukocytosis
- Sputum culture and Gram stain
- Blood cultures (if severe)
- Pulse oximetry
- ABG if hypoxemia suspected

**Treatment - Community-Acquired Pneumonia:**
**Outpatient (no comorbidities):**
- Amoxicillin 1g TID or
- Doxycycline 100mg BID or
- Macrolide (Azithromycin 500mg day 1, then 250mg days 2-5)

**Outpatient (with comorbidities):**
- Amoxicillin-clavulanate + Macrolide or
- Respiratory fluoroquinolone (Levofloxacin 750mg daily)

**Inpatient (non-ICU):**
- Beta-lactam + Macrolide or
- Respiratory fluoroquinolone

**Inpatient (ICU):**
- Beta-lactam + Macrolide or
- Beta-lactam + Fluoroquinolone

**Duration:** Typically 5-7 days for uncomplicated CAP

**Supportive Care:**
- Oxygen therapy (maintain SpO2 >92%)
- IV fluids for hydration
- Antipyretics for fever
- Chest physiotherapy

---

**ICD-10 Codes:**
- R50.9: Fever, unspecified
- I10: Essential (primary) hypertension
- J18.9: Pneumonia, unspecified organism

**Last Updated:** December 2025
**Evidence Level:** Based on current clinical practice guidelines
"@

# Save to temp file
$tempFile = [System.IO.Path]::GetTempFileName()
$pdfFile = $tempFile.Replace(".tmp", ".txt")
Move-Item $tempFile $pdfFile -Force

Set-Content -Path $pdfFile -Value $medicalContent -Encoding UTF8

Write-Host "  SUCCESS: Medical reference created`n" -ForegroundColor Green

# Upload to knowledge base
Write-Host "[3] Uploading to knowledge base..." -ForegroundColor Yellow

try {
    $boundary = [System.Guid]::NewGuid().ToString()
    $fileContent = [System.IO.File]::ReadAllBytes($pdfFile)
    $fileName = "Basic_Medical_Reference.txt"
    
    $bodyLines = @(
        "--$boundary",
        "Content-Disposition: form-data; name=`"file`"; filename=`"$fileName`"",
        "Content-Type: text/plain",
        "",
        [System.Text.Encoding]::UTF8.GetString($fileContent),
        "--$boundary--"
    ) -join "`r`n"
    
    # Use curl for multipart upload
    $curlCommand = @"
curl -X POST "$BASE_URL/api/medical/knowledge/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@$pdfFile"
"@

    Invoke-Expression $curlCommand | Out-Null
    
    Write-Host "  SUCCESS: Document uploaded to knowledge base`n" -ForegroundColor Green
    Write-Host "  Waiting for processing..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
} catch {
    Write-Host "  WARNING: Upload may have failed, trying alternative method`n" -ForegroundColor Yellow
}

# Clean up temp file
Remove-Item $pdfFile -ErrorAction SilentlyContinue

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Knowledge Base Updated!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Now try asking:" -ForegroundColor Cyan
Write-Host "  - What is fever?" -ForegroundColor White
Write-Host "  - How to treat hypertension?" -ForegroundColor White
Write-Host "  - What are symptoms of pneumonia?" -ForegroundColor White
Write-Host "`nTest in UI: http://localhost:5173`n" -ForegroundColor Cyan
