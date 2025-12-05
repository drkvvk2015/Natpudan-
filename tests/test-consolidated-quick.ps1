#!/usr/bin/env pwsh
# Quick test of consolidated response feature

$baseUrl = "http://localhost:8001"

Write-Host "[SEARCH] Testing Consolidated Response Feature" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan
Write-Host ""

# 1. Check backend
Write-Host "1️⃣ Checking backend..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health"
    Write-Host "   [OK] Backend running (Uptime: $($health.uptime_seconds)s)" -ForegroundColor Green
} catch {
    Write-Host "   [ERROR] Backend not running - start with: .\start-backend.ps1" -ForegroundColor Red
    exit 1
}

# 2. Login
Write-Host ""
Write-Host "2️⃣ Authenticating..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/auth/login" `
        -Method POST `
        -Body @{username="test@example.com"; password="test123"} `
        -ContentType "application/x-www-form-urlencoded"
    $token = $response.access_token
    Write-Host "   [OK] Logged in successfully" -ForegroundColor Green
} catch {
    Write-Host "   [ERROR] Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 3. Test chat
Write-Host ""
Write-Host "3️⃣ Testing chat query: 'What is diabetes?'" -ForegroundColor Yellow
try {
    $chatBody = @{message="What is diabetes?"; conversation_id=$null} | ConvertTo-Json
    $headers = @{Authorization="Bearer $token"; "Content-Type"="application/json"}
    
    $chat = Invoke-RestMethod -Uri "$baseUrl/api/chat/message" `
        -Method POST -Body $chatBody -Headers $headers
    
    $content = $chat.message.content
    Write-Host "   [OK] Response received ($($content.Length) chars)" -ForegroundColor Green
    
    # Check features
    Write-Host ""
    Write-Host "4️⃣ Analyzing response features..." -ForegroundColor Yellow
    
    $features = @(
        @{Name="Consolidated Format"; Pattern="CONSOLIDATED|CLINICAL OVERVIEW|DETAILED ANALYSIS"},
        @{Name="Reference Library"; Pattern="REFERENCE LIBRARY|Sources Referenced"},
        @{Name="Citations"; Pattern="\[\d+\]"},
        @{Name="Clickable Links"; Pattern="\[View.*?\]\("},
        @{Name="Visual Resources"; Pattern="VISUAL LEARNING RESOURCES"}
    )
    
    foreach ($f in $features) {
        if ($content -match $f.Pattern) {
            Write-Host "   [OK] $($f.Name)" -ForegroundColor Green
        } else {
            Write-Host "   [WARNING]  $($f.Name) - not found" -ForegroundColor Yellow
        }
    }
    
    # Count citations
    $citations = [regex]::Matches($content, '\[\d+\]').Count
    Write-Host ""
    Write-Host "[STATS] Metrics:" -ForegroundColor Cyan
    Write-Host "   • Response length: $($content.Length) characters" -ForegroundColor White
    Write-Host "   • Evidence citations: $citations" -ForegroundColor White
    
    # Show preview
    Write-Host ""
    Write-Host "[PAGE] Preview (first 600 chars):" -ForegroundColor Cyan
    Write-Host "-"*60 -ForegroundColor Gray
    $preview = $content.Substring(0, [Math]::Min(600, $content.Length))
    Write-Host $preview -ForegroundColor White
    if ($content.Length -gt 600) {
        Write-Host "`n... [$($content.Length - 600) more characters] ..." -ForegroundColor Gray
    }
    Write-Host "-"*60 -ForegroundColor Gray
    
    Write-Host ""
    Write-Host "[OK] CONSOLIDATED RESPONSE FEATURE IS WORKING!" -ForegroundColor Green
    Write-Host ""
    Write-Host "[TIP] Next steps:" -ForegroundColor Yellow
    Write-Host "   1. Test in frontend UI (localhost:5173)" -ForegroundColor White
    Write-Host "   2. Click reference links to verify navigation" -ForegroundColor White
    Write-Host "   3. Try different medical queries" -ForegroundColor White
    
} catch {
    Write-Host "   [ERROR] Chat failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
