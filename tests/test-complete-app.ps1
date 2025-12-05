# COMPREHENSIVE APP TESTING SCRIPT
param(
    [switch]$StartBackend = $false
)

Write-Host "`n" + ("="*70) -ForegroundColor Cyan
Write-Host "🧪 NATPUDAN AI - COMPREHENSIVE APPLICATION TEST" -ForegroundColor Cyan
Write-Host ("="*70) -ForegroundColor Cyan

$baseUrl = "http://localhost:8001"
$passed = 0
$failed = 0
$warnings = 0

# Helper function
function Test-Endpoint {
    param($Name, $ScriptBlock)
    Write-Host "`n[LIST] Testing: $Name" -ForegroundColor Yellow
    try {
        & $ScriptBlock
        $script:passed++
        Write-Host "   [OK] PASSED" -ForegroundColor Green
        return $true
    } catch {
        $script:failed++
        Write-Host "   [ERROR] FAILED: $_" -ForegroundColor Red
        return $false
    }
}

# 1. Check Backend
Write-Host "`n1️⃣ BACKEND STATUS CHECK" -ForegroundColor Cyan
Write-Host ("-"*70)

try {
    $health = Invoke-RestMethod "$baseUrl/health" -TimeoutSec 3
    Write-Host "[OK] Backend is RUNNING" -ForegroundColor Green
    Write-Host "   Uptime: $($health.uptime_seconds) seconds" -ForegroundColor Gray
    Write-Host "   Status: $($health.status)" -ForegroundColor Gray
    $passed++
} catch {
    Write-Host "[ERROR] Backend is NOT RUNNING" -ForegroundColor Red
    if ($StartBackend) {
        Write-Host "`n[ROCKET] Starting backend..." -ForegroundColor Yellow
        cd "$PSScriptRoot\backend"
        $job = Start-Job {
            & 'D:\Users\CNSHO\Documents\GitHub\Natpudan-\.venv311\Scripts\python.exe' -m uvicorn app.main_simple:app --host 127.0.0.1 --port 8001
        }
        Write-Host "   Waiting 10 seconds for startup..." -ForegroundColor Gray
        Start-Sleep -Seconds 10
        
        try {
            $health = Invoke-RestMethod "$baseUrl/health" -TimeoutSec 3
            Write-Host "[OK] Backend started successfully!" -ForegroundColor Green
            $passed++
        } catch {
            Write-Host "[ERROR] Backend failed to start" -ForegroundColor Red
            Write-Host "`n[WARNING]  Cannot continue testing without backend" -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host "`n[WARNING]  Run with -StartBackend to auto-start" -ForegroundColor Yellow
        Write-Host "[WARNING]  Or manually run: .\start-backend.ps1" -ForegroundColor Yellow
        exit 1
    }
}

# 2. Authentication Tests
Write-Host "`n2️⃣ AUTHENTICATION TESTS" -ForegroundColor Cyan
Write-Host ("-"*70)

$global:token = $null

Test-Endpoint "Login with test credentials" {
    $loginBody = @{
        email = "test@example.com"
        password = "test123"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod "$baseUrl/api/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
    
    if (-not $response.access_token) {
        throw "No access token returned"
    }
    
    $global:token = $response.access_token
    Write-Host "   User: $($response.user.email)" -ForegroundColor Gray
    Write-Host "   Role: $($response.user.role)" -ForegroundColor Gray
    Write-Host "   Token: $($global:token.Substring(0, 20))..." -ForegroundColor Gray
}

if (-not $global:token) {
    Write-Host "`n[ERROR] Cannot continue without authentication token" -ForegroundColor Red
    exit 1
}

$headers = @{
    Authorization = "Bearer $global:token"
}

# 3. Knowledge Base Tests
Write-Host "`n3️⃣ KNOWLEDGE BASE TESTS" -ForegroundColor Cyan
Write-Host ("-"*70)

$kbStats = $null

Test-Endpoint "Knowledge Base Statistics" {
    $script:kbStats = Invoke-RestMethod "$baseUrl/api/medical/knowledge/statistics" -Method GET
    
    Write-Host "   📚 Total Documents: $($kbStats.total_documents)" -ForegroundColor Gray
    Write-Host "   📝 Total Chunks: $($kbStats.total_chunks)" -ForegroundColor Gray
    Write-Host "   🎓 Knowledge Level: $($kbStats.knowledge_level)" -ForegroundColor Gray
    Write-Host "   ⏱️  Avg Response Time: $($kbStats.avg_response_time_ms)ms" -ForegroundColor Gray
    
    if ($kbStats.total_chunks -eq 0) {
        $script:warnings++
        Write-Host "   [WARNING]  WARNING: No chunks loaded!" -ForegroundColor Yellow
    }
}

Test-Endpoint "Knowledge Base Search" {
    $searchBody = @{
        query = "diabetes symptoms"
        top_k = 5
    } | ConvertTo-Json
    
    $results = Invoke-RestMethod "$baseUrl/api/medical/knowledge/search" -Method POST -Body $searchBody -ContentType "application/json"
    
    Write-Host "   Found: $($results.results.Count) results" -ForegroundColor Gray
    
    if ($results.results.Count -eq 0) {
        $script:warnings++
        Write-Host "   [WARNING]  WARNING: Search returned no results" -ForegroundColor Yellow
    } else {
        Write-Host "   Top result: $($results.results[0].title)" -ForegroundColor Gray
    }
}

# 4. Chat Tests
Write-Host "`n4️⃣ CHAT SYSTEM TESTS" -ForegroundColor Cyan
Write-Host ("-"*70)

$chatResponse = $null

Test-Endpoint "Basic Chat Query" {
    $chatBody = @{
        message = "What is diabetes?"
        conversation_id = $null
    } | ConvertTo-Json
    
    $script:chatResponse = Invoke-RestMethod "$baseUrl/api/chat/message" -Method POST -Body $chatBody -ContentType "application/json" -Headers $headers
    
    if (-not $chatResponse.message) {
        throw "No message in response"
    }
    
    $msgLength = $chatResponse.message.Length
    Write-Host "   Response length: $msgLength characters" -ForegroundColor Gray
    Write-Host "   Conversation ID: $($chatResponse.conversation_id)" -ForegroundColor Gray
}

# 5. Visual Resources Tests
Write-Host "`n5️⃣ VISUAL RESOURCES TESTS" -ForegroundColor Cyan
Write-Host ("-"*70)

if ($chatResponse) {
    Test-Endpoint "Visual Resources in Chat Response" {
        $msg = $chatResponse.message
        
        # Check for visual section
        if ($msg -match '📺.*VISUAL LEARNING RESOURCES') {
            Write-Host "   [OK] Visual section present" -ForegroundColor Gray
            
            # Check search term
            if ($msg -match 'Search Term:\s*(.+)') {
                $searchTerm = $matches[1].Trim()
                Write-Host "   [SEARCH] Search Term: '$searchTerm'" -ForegroundColor Gray
                
                # Check if clean (no database references)
                if ($searchTerm -like '*Medical Database*' -or $searchTerm -like '*Local Database*') {
                    $script:warnings++
                    Write-Host "   [WARNING]  WARNING: Search term contains database reference" -ForegroundColor Yellow
                } else {
                    Write-Host "   [OK] Search term is clean" -ForegroundColor Gray
                }
            }
            
            # Count resources
            $imageCount = ([regex]::Matches($msg, '🖼️')).Count
            $videoCount = ([regex]::Matches($msg, '🎬')).Count
            
            Write-Host "   🖼️  Image sources: $imageCount" -ForegroundColor Gray
            Write-Host "   🎬  Video sources: $videoCount" -ForegroundColor Gray
            
            if ($imageCount -eq 0 -or $videoCount -eq 0) {
                $script:warnings++
                Write-Host "   [WARNING]  WARNING: Missing image or video sources" -ForegroundColor Yellow
            }
            
            # Check for clickable links
            $linkCount = ([regex]::Matches($msg, '\[.*?\]\(http')).Count
            Write-Host "   🔗 Clickable links: $linkCount" -ForegroundColor Gray
            
        } else {
            throw "Visual resources section not found in response"
        }
    }
    
    Test-Endpoint "Medical Condition Extraction" {
        $msg = $chatResponse.message
        
        # Check if we have knowledge base results
        if ($msg -match '🏥.*MEDICAL KNOWLEDGE BASE') {
            Write-Host "   [OK] KB search results present" -ForegroundColor Gray
            
            # Count references
            $refCount = ([regex]::Matches($msg, '\[(\d+)\]')).Count
            Write-Host "   📚 References cited: $refCount" -ForegroundColor Gray
            
        } else {
            $script:warnings++
            Write-Host "   [WARNING]  WARNING: KB results not in response" -ForegroundColor Yellow
        }
    }
}

# 6. Additional API Tests
Write-Host "`n6️⃣ ADDITIONAL API ENDPOINTS" -ForegroundColor Cyan
Write-Host ("-"*70)

Test-Endpoint "API Root Endpoint" {
    $root = Invoke-RestMethod "$baseUrl/" -Method GET
    Write-Host "   Version: $($root.version)" -ForegroundColor Gray
    Write-Host "   Message: $($root.message)" -ForegroundColor Gray
}

Test-Endpoint "API Documentation Available" {
    $docs = Invoke-WebRequest "$baseUrl/docs" -Method GET -TimeoutSec 5
    if ($docs.StatusCode -ne 200) {
        throw "Docs not accessible"
    }
    Write-Host "   📖 API docs accessible at /docs" -ForegroundColor Gray
}

# Final Summary
Write-Host "`n" + ("="*70) -ForegroundColor Cyan
Write-Host "[STATS] TEST SUMMARY" -ForegroundColor Cyan
Write-Host ("="*70) -ForegroundColor Cyan

Write-Host "`n[OK] Passed:   $passed" -ForegroundColor Green
Write-Host "[ERROR] Failed:   $failed" -ForegroundColor $(if ($failed -gt 0) { 'Red' } else { 'Gray' })
Write-Host "[WARNING]  Warnings: $warnings" -ForegroundColor $(if ($warnings -gt 0) { 'Yellow' } else { 'Gray' })

$total = $passed + $failed
$successRate = if ($total -gt 0) { [math]::Round(($passed / $total) * 100, 1) } else { 0 }

Write-Host "`n[CHART] Success Rate: $successRate%" -ForegroundColor $(if ($successRate -ge 80) { 'Green' } elseif ($successRate -ge 60) { 'Yellow' } else { 'Red' })

if ($failed -eq 0 -and $warnings -eq 0) {
    Write-Host "`n[PARTY] ALL TESTS PASSED - APPLICATION IS FULLY FUNCTIONAL!" -ForegroundColor Green
} elseif ($failed -eq 0) {
    Write-Host "`n[OK] All tests passed but there are $warnings warnings to review" -ForegroundColor Yellow
} else {
    Write-Host "`n[WARNING]  Some tests failed - review errors above" -ForegroundColor Red
}

Write-Host "`n" + ("="*70) -ForegroundColor Cyan

# Return exit code
if ($failed -gt 0) {
    exit 1
} else {
    exit 0
}
