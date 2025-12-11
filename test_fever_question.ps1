# Test Improved AI Chat - "What is fever?"

$BASE_URL = "http://localhost:8000"

Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host " Testing AI Chat Improvements" -ForegroundColor Cyan
Write-Host "======================================`n" -ForegroundColor Cyan

# Login
Write-Host "[1] Logging in..." -ForegroundColor Yellow
$loginBody = @{
    email = "admin@example.com"
    password = "admin123"
} | ConvertTo-Json

try {
    $login = Invoke-RestMethod -Uri "$BASE_URL/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    $TOKEN = $login.access_token
    Write-Host "  SUCCESS: Logged in as admin`n" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Login failed - $_`n" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $TOKEN"
    "Content-Type" = "application/json"
}

# Test: What is fever?
Write-Host "[2] Testing: 'WHAT IS FEVER?'" -ForegroundColor Yellow
$chatBody = @{
    message = "WHAT IS FEVER?"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/chat/message" -Method Post -Body $chatBody -Headers $headers
    
    Write-Host "  SUCCESS: Got AI response`n" -ForegroundColor Green
    
    # Display response
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host " AI Response:" -ForegroundColor Cyan
    Write-Host "======================================" -ForegroundColor Cyan
    
    # Extract and display the content
    $content = $response.message.content
    
    # Show first 1500 characters
    if ($content.Length -gt 1500) {
        Write-Host $content.Substring(0, 1500) -ForegroundColor White
        Write-Host "`n... [response continues, total length: $($content.Length) characters]" -ForegroundColor Gray
    } else {
        Write-Host $content -ForegroundColor White
    }
    
    Write-Host "`n======================================" -ForegroundColor Cyan
    Write-Host " Test Complete!" -ForegroundColor Green
    Write-Host "======================================`n" -ForegroundColor Cyan
    
    # Analysis
    Write-Host "ANALYSIS:" -ForegroundColor Yellow
    if ($content -match "(?i)fever.*?(is|definition|elevated|temperature|pyrexia)") {
        Write-Host "  [OK] Response includes fever definition" -ForegroundColor Green
    } else {
        Write-Host "  [WARNING] May not include clear definition" -ForegroundColor Yellow
    }
    
    if ($content.Length -gt 200) {
        Write-Host "  [OK] Comprehensive response ($($content.Length) characters)" -ForegroundColor Green
    } else {
        Write-Host "  [WARNING] Brief response" -ForegroundColor Yellow
    }
    
    if ($content -match "\[1\]|\[2\]|\[3\]") {
        Write-Host "  [OK] Includes source citations" -ForegroundColor Green
    } else {
        Write-Host "  [INFO] No knowledge base citations (using general AI knowledge)" -ForegroundColor Cyan
    }
    
} catch {
    Write-Host "  ERROR: Chat failed - $_`n" -ForegroundColor Red
    Write-Host "Error Details:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Write-Host "`nTo test in the UI: http://localhost:5173`n" -ForegroundColor Cyan
