# Quick Diagnostic and Fix Script

Write-Host "`n🔍 DIAGNOSTIC REPORT" -ForegroundColor Cyan
Write-Host "="*60

# Test 1: Check backend response
Write-Host "`n1. Testing chat endpoint..." -ForegroundColor Yellow
$headers = @{Authorization="Bearer test_token_placeholder"}
$body = '{"message":"test","conversation_id":null}'

try {
    # First login to get real token
    $login = '{"email":"test@example.com","password":"test123"}'
    $auth = Invoke-RestMethod "http://localhost:8001/api/auth/login" -Method POST -Body $login -ContentType "application/json"
    $headers = @{Authorization="Bearer $($auth.access_token)"}
    
    $resp = Invoke-RestMethod "http://localhost:8001/api/chat/message" -Method POST -Body $body -ContentType "application/json" -Headers $headers
    Write-Host "Response length: $($resp.message.Length) chars" -ForegroundColor Cyan
    
    if ($resp.message.Length -lt 10) {
        Write-Host "⚠️  Very short response - possible error" -ForegroundColor Yellow
        Write-Host "Response: '$($resp.message)'" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}

# Test 2: Check KB search
Write-Host "`n2. Testing KB search endpoint..." -ForegroundColor Yellow
$searchBody = '{"query":"diabetes","top_k":3,"min_score":0.0}'

try {
    $search = Invoke-RestMethod "http://localhost:8001/api/medical/knowledge/search" -Method POST -Body $searchBody -ContentType "application/json"
    
    if ($search.error) {
        Write-Host "❌ Search returned error: $($search.error)" -ForegroundColor Red
    } elseif ($search.results) {
        Write-Host "✅ Search OK: $($search.results.Count) results" -ForegroundColor Green
    } else {
        Write-Host "⚠️  No results field in response" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Search failed: $_" -ForegroundColor Red
    if ($_.ErrorDetails) {
        Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
}

# Test 3: Check visual service
Write-Host "`n3. Checking visual service..." -ForegroundColor Yellow
$testQuery = '{"message":"What is fever?","conversation_id":null}'

try {
    $resp2 = Invoke-RestMethod "http://localhost:8001/api/chat/message" -Method POST -Body $testQuery -ContentType "application/json" -Headers $headers
    
    if ($resp2.message -match 'VISUAL LEARNING') {
        Write-Host "✅ Visual resources working" -ForegroundColor Green
    } else {
        Write-Host "❌ No visual resources in response" -ForegroundColor Red
    }
    
    if ($resp2.message -match 'MEDICAL KNOWLEDGE BASE') {
        Write-Host "✅ KB search working" -ForegroundColor Green
    } else {
        Write-Host "❌ No KB results in response" -ForegroundColor Red  
    }
} catch {
    Write-Host "❌ Chat test failed: $_" -ForegroundColor Red
}

Write-Host "`n" + ("="*60)
Write-Host "📊 DIAGNOSIS COMPLETE" -ForegroundColor Cyan
