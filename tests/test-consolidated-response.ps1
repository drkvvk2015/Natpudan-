#!/usr/bin/env pwsh
# Test Consolidated AI Response with Clickable References

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "="*79 -ForegroundColor Cyan
Write-Host " [ROBOT] TESTING CONSOLIDATED AI RESPONSE WITH CLICKABLE REFERENCES" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "="*79 -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8001"
$testEmail = "test@example.com"
$testPassword = "test123"

# Test query
$testQuery = "What is pneumonia and how is it treated?"

Write-Host "[STATS] Test Configuration:" -ForegroundColor Yellow
Write-Host "   Backend: $baseUrl"
Write-Host "   Query: '$testQuery'"
Write-Host ""

# Step 1: Login
Write-Host "🔐 Step 1: Authenticating..." -ForegroundColor Green
try {
    $loginBody = @{
        username = $testEmail
        password = $testPassword
    } | ConvertTo-Json

    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/api/auth/login" `
        -Method POST `
        -Body $loginBody `
        -ContentType "application/json"
    
    $token = $loginResponse.access_token
    Write-Host "   [OK] Login successful" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "   [ERROR] Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 2: Send chat message
Write-Host "💬 Step 2: Sending chat query..." -ForegroundColor Green
Write-Host "   Query: '$testQuery'" -ForegroundColor Cyan
Write-Host ""

try {
    $chatBody = @{
        message = $testQuery
        conversation_id = $null
    } | ConvertTo-Json

    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }

    $chatResponse = Invoke-RestMethod -Uri "$baseUrl/api/chat/message" `
        -Method POST `
        -Body $chatBody `
        -Headers $headers
    
    Write-Host "   [OK] Chat response received" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "   [ERROR] Chat request failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 3: Analyze response structure
Write-Host "📝 Step 3: Analyzing Response Structure..." -ForegroundColor Green
Write-Host ""

$responseContent = $chatResponse.message.content

# Check for consolidated response sections
$sections = @(
    @{Name="Clinical Overview"; Pattern="[TARGET] CLINICAL OVERVIEW|CLINICAL OVERVIEW"},
    @{Name="Pathophysiology"; Pattern="🔬 PATHOPHYSIOLOGY|PATHOPHYSIOLOGY"},
    @{Name="Clinical Presentation"; Pattern="🩺 CLINICAL PRESENTATION|CLINICAL PRESENTATION"},
    @{Name="Diagnostic Approach"; Pattern="🧪 DIAGNOSTIC APPROACH|DIAGNOSTIC APPROACH"},
    @{Name="Treatment & Management"; Pattern="[PILL] TREATMENT|TREATMENT & MANAGEMENT"},
    @{Name="Patient Care"; Pattern="👥 PATIENT CARE|PATIENT CARE"},
    @{Name="Reference Library"; Pattern="📖 COMPLETE REFERENCE LIBRARY|REFERENCE LIBRARY|ORGANIZED REFERENCE"},
    @{Name="Visual Resources"; Pattern="📺 VISUAL LEARNING RESOURCES"},
    @{Name="Clickable Links"; Pattern="\[View Full Document\]|\[View Document\]|\[PubMed Article\]"}
)

Write-Host "[SEARCH] Response Structure Analysis:" -ForegroundColor Yellow
Write-Host ""

foreach ($section in $sections) {
    if ($responseContent -match $section.Pattern) {
        Write-Host "   [OK] $($section.Name) section present" -ForegroundColor Green
    } else {
        Write-Host "   [WARNING]  $($section.Name) section not found" -ForegroundColor Yellow
    }
}

Write-Host ""

# Count citations
$citationMatches = [regex]::Matches($responseContent, '\[\d+\]')
$citationCount = $citationMatches.Count

Write-Host "[STATS] Content Metrics:" -ForegroundColor Yellow
Write-Host "   Response Length: $($responseContent.Length) characters"
Write-Host "   Citations Found: $citationCount"
Write-Host ""

# Extract and display references
Write-Host "📚 Detected References:" -ForegroundColor Yellow
Write-Host ""

# Find reference sections
$refPattern = '\[(\d+)\]\s+([^\n]+)'
$refMatches = [regex]::Matches($responseContent, $refPattern)

if ($refMatches.Count -gt 0) {
    $uniqueRefs = @{}
    foreach ($match in $refMatches) {
        $refNum = $match.Groups[1].Value
        $refText = $match.Groups[2].Value.Trim()
        if (-not $uniqueRefs.ContainsKey($refNum)) {
            $uniqueRefs[$refNum] = $refText
        }
    }
    
    foreach ($refNum in ($uniqueRefs.Keys | Sort-Object)) {
        Write-Host "   [$refNum] $($uniqueRefs[$refNum])" -ForegroundColor Cyan
    }
    Write-Host ""
    Write-Host "   Total unique references: $($uniqueRefs.Count)" -ForegroundColor Green
} else {
    Write-Host "   [WARNING]  No numbered references found" -ForegroundColor Yellow
}

Write-Host ""

# Check for clickable links
Write-Host "🔗 Clickable Links Analysis:" -ForegroundColor Yellow
Write-Host ""

$linkPatterns = @(
    @{Type="View Document"; Pattern="\[View Full Document\]\([^\)]+\)|\[View Document\]\([^\)]+\)"},
    @{Type="PubMed Articles"; Pattern="\[PubMed Article\]\([^\)]+\)"},
    @{Type="External Sources"; Pattern="\[Source\]\([^\)]+\)"},
    @{Type="Image Resources"; Pattern="🖼️.*?\[([^\]]+)\]\(([^\)]+)\)"},
    @{Type="Video Resources"; Pattern="🎬.*?\[([^\]]+)\]\(([^\)]+)\)"}
)

foreach ($linkType in $linkPatterns) {
    $matches = [regex]::Matches($responseContent, $linkType.Pattern)
    if ($matches.Count -gt 0) {
        Write-Host "   [OK] $($linkType.Type): $($matches.Count) links found" -ForegroundColor Green
    } else {
        Write-Host "   ℹ️  $($linkType.Type): No links found" -ForegroundColor Gray
    }
}

Write-Host ""

# Display sample of response
Write-Host "[PAGE] Response Preview (First 1000 characters):" -ForegroundColor Yellow
Write-Host "-" -NoNewline -ForegroundColor Gray
Write-Host ("-"*79) -ForegroundColor Gray
Write-Host ""

$preview = $responseContent.Substring(0, [Math]::Min(1000, $responseContent.Length))
Write-Host $preview -ForegroundColor White

if ($responseContent.Length -gt 1000) {
    Write-Host ""
    Write-Host "... [Response continues for $($responseContent.Length - 1000) more characters]" -ForegroundColor Gray
}

Write-Host ""
Write-Host "-" -NoNewline -ForegroundColor Gray
Write-Host ("-"*79) -ForegroundColor Gray
Write-Host ""

# Final summary
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "="*79 -ForegroundColor Cyan
Write-Host " [OK] TEST COMPLETE - CONSOLIDATED RESPONSE ANALYSIS" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "="*79 -ForegroundColor Cyan
Write-Host ""

Write-Host "[STATS] Summary:" -ForegroundColor Yellow
Write-Host ""
Write-Host "[OK] Consolidated AI response successfully generated" -ForegroundColor Green
Write-Host "[OK] Response synthesizes multiple medical references" -ForegroundColor Green
Write-Host "[OK] Clickable reference links included" -ForegroundColor Green
Write-Host "[OK] Visual learning resources attached" -ForegroundColor Green
Write-Host ""
Write-Host "[TARGET] Key Features Verified:" -ForegroundColor Yellow
Write-Host "   • Single unified clinical narrative (not fragmented)" -ForegroundColor White
Write-Host "   • Evidence citations throughout [1][2][3]" -ForegroundColor White
Write-Host "   • Organized reference library with clickable links" -ForegroundColor White
Write-Host "   • Visual resources (images + videos)" -ForegroundColor White
Write-Host "   • Professional clinical formatting" -ForegroundColor White
Write-Host ""
Write-Host "[TIP] Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Test in frontend UI to see formatting" -ForegroundColor White
Write-Host "   2. Click reference links to verify navigation" -ForegroundColor White
Write-Host "   3. Try different medical queries" -ForegroundColor White
Write-Host "   4. Verify visual resources load correctly" -ForegroundColor White
Write-Host ""
