# Test Patient Intake API
Write-Host "Testing Patient Intake API..." -ForegroundColor Cyan

# Test data
$patientData = @{
    name = "John Doe"
    age = "45"
    gender = "Male"
    bloodType = "O+"
    travelHistory = @(
        @{
            id = "1"
            destination = "Asia - Thailand"
            departureDate = "2024-10-15"
            returnDate = "2024-10-25"
            duration = "10 days"
            purpose = "Tourism"
            activities = @("Beach Activities", "Street Food", "Urban Tourism")
        }
    )
    familyHistory = @(
        @{
            id = "1"
            relationship = "Father"
            condition = "Diabetes Type 2"
            ageOfOnset = "50 years"
            duration = "15 years"
            status = "ongoing"
            notes = "Well controlled with medication"
        },
        @{
            id = "2"
            relationship = "Mother"
            condition = "Hypertension"
            ageOfOnset = "55 years"
            duration = "10 years"
            status = "ongoing"
            notes = "On medication"
        }
    )
} | ConvertTo-Json -Depth 10

Write-Host "`nSending POST request to create patient intake..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8001/api/medical/patient-intake" `
        -Method Post `
        -ContentType "application/json" `
        -Body $patientData

    Write-Host "`n[OK] Patient intake created successfully!" -ForegroundColor Green
    Write-Host "Intake ID: $($response.intake_id)" -ForegroundColor Cyan
    Write-Host "Patient Name: $($response.name)" -ForegroundColor Cyan
    Write-Host "Age: $($response.age)" -ForegroundColor Cyan
    Write-Host "Gender: $($response.gender)" -ForegroundColor Cyan
    Write-Host "Blood Type: $($response.bloodType)" -ForegroundColor Cyan
    Write-Host "Travel History Count: $($response.travelHistory.Count)" -ForegroundColor Cyan
    Write-Host "Family History Count: $($response.familyHistory.Count)" -ForegroundColor Cyan
    Write-Host "Created At: $($response.created_at)" -ForegroundColor Cyan

    # Test GET endpoint
    Write-Host "`n`nTesting GET endpoint..." -ForegroundColor Yellow
    $intakeId = $response.intake_id
    $getResponse = Invoke-RestMethod -Uri "http://localhost:8001/api/medical/patient-intake/$intakeId" `
        -Method Get

    Write-Host "`n[OK] Patient intake retrieved successfully!" -ForegroundColor Green
    Write-Host "Retrieved Name: $($getResponse.name)" -ForegroundColor Cyan
    
    Write-Host "`nTravel History:" -ForegroundColor Yellow
    foreach ($travel in $getResponse.travelHistory) {
        Write-Host "  - $($travel.destination) ($($travel.duration))" -ForegroundColor White
        Write-Host "    Purpose: $($travel.purpose)" -ForegroundColor Gray
    }

    Write-Host "`nFamily History:" -ForegroundColor Yellow
    foreach ($family in $getResponse.familyHistory) {
        Write-Host "  - $($family.relationship): $($family.condition)" -ForegroundColor White
        Write-Host "    Status: $($family.status), Onset: $($family.ageOfOnset)" -ForegroundColor Gray
    }

    Write-Host "`n`n[OK] All API tests passed!" -ForegroundColor Green

} catch {
    Write-Host "`n✗ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Response: $($_.ErrorDetails.Message)" -ForegroundColor Red
}
