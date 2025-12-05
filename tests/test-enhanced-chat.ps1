# Test Enhanced Chat with Detailed Responses
Write-Host "🧪 Testing Enhanced Chat with Knowledge Base Integration..." -ForegroundColor Cyan

$baseUrl = "http://localhost:8001"
$apiUrl = "$baseUrl/api"
$email = "test@example.com"
$password = "test123"

Write-Host "[LIST] Step 1: Authentication..." -ForegroundColor Yellow

$loginBody = @{ username = $email; password = $password } | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$apiUrl/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    $token = $loginResponse.access_token
    Write-Host "[OK] Authenticated successfully" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Authentication failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}


$headers = @{ "Authorization" = "Bearer $token"; "Content-Type" = "application/json" }

Write-Host "[LIST] Step 2: Sending Test Medical Query..." -ForegroundColor Yellow
$testQuery = "What are the first-line treatments for type 2 diabetes?"
$chatBody = @{ message = $testQuery; conversation_id = $null } | ConvertTo-Json

Write-Host "💬 Query: $testQuery" -ForegroundColor Cyan
Write-Host "[WAIT] Waiting for response..." -ForegroundColor Yellow


try {
    $response = Invoke-RestMethod -Uri "$apiUrl/chat/message" -Method Post -Body $chatBody -ContentType "application/json" -Headers $headers
    
    Write-Host "`n[OK] Response Received!" -ForegroundColor Green
    Write-Host "`n💬 Message:" -ForegroundColor Yellow
    Write-Host $response.message -ForegroundColor White
    
    $responseLength = $response.message.Length
    Write-Host "`n📏 Response Length: $responseLength characters" -ForegroundColor Cyan
    
    $hasCitations = $response.message -match '\[\d+\]'
    if ($hasCitations) {
        Write-Host "[OK] Citations Found" -ForegroundColor Green
    } else {
        Write-Host "[WARNING]  No Citations" -ForegroundColor Yellow
    }
    
    $hasSources = $response.message -match 'MEDICAL KNOWLEDGE BASE'
    if ($hasSources) {
        Write-Host "[OK] KB Sources Found" -ForegroundColor Green
    } else {
        Write-Host "[WARNING]  No KB Headers" -ForegroundColor Yellow
    }
    
    $hasStructure = $response.message -match 'EXECUTIVE SUMMARY|DETAILED ANALYSIS|CLINICAL GUIDANCE'
    if ($hasStructure) {
        Write-Host "[OK] Structured Format" -ForegroundColor Green
    } else {
        Write-Host "[WARNING]  Basic Format" -ForegroundColor Yellow
    }
    
    Write-Host "`n[OK] TEST COMPLETED!" -ForegroundColor Green
    
} catch {
    Write-Host "`n[ERROR] Chat request failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
