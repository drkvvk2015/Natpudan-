# Test FEVER query with fixed visual resources

Write-Host "`n🧪 Testing FEVER Query - Visual Resources Fix" -ForegroundColor Cyan
Write-Host "=" * 60

# Login first
Write-Host "`n1️⃣ Logging in..." -ForegroundColor Yellow
$loginBody = @{
    email = "test@example.com"
    password = "test123"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8001/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    $token = $loginResponse.access_token
    Write-Host "[OK] Login successful!" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Login failed: $_" -ForegroundColor Red
    exit 1
}

# Test FEVER query
Write-Host "`n2️⃣ Testing 'WHAT IS FEVER?' query..." -ForegroundColor Yellow
$headers = @{Authorization="Bearer $token"}
$queryBody = @{
    message = "WHAT IS FEVER?"
    conversation_id = $null
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8001/api/chat/message" -Method Post -Body $queryBody -ContentType "application/json" -Headers $headers
    $message = $response.message
    
    Write-Host "[OK] Query successful!" -ForegroundColor Green
    
    # Check for visual resources section
    Write-Host "`n3️⃣ Checking Visual Resources..." -ForegroundColor Yellow
    
    if ($message -match '📺 \*\*VISUAL LEARNING RESOURCES\*\*') {
        Write-Host "[OK] Visual resources section found!" -ForegroundColor Green
        
        # Extract search term
        if ($message -match 'Search Term:\s*(.+)') {
            $searchTerm = $matches[1].Trim()
            Write-Host "`n[SEARCH] Search Term: '$searchTerm'" -ForegroundColor Cyan
            
            # Check if it's a good search term (not the database reference)
            if ($searchTerm -like '*Medical Database*' -or $searchTerm -like '*Local Database*') {
                Write-Host "[ERROR] ERROR: Still extracting database reference!" -ForegroundColor Red
            } else {
                Write-Host "[OK] Search term looks good!" -ForegroundColor Green
            }
        }
        
        # Extract visual content section
        $visualStart = $message.IndexOf('📺 **VISUAL LEARNING RESOURCES**')
        if ($visualStart -ge 0) {
            $visualSection = $message.Substring($visualStart, [Math]::Min(1200, $message.Length - $visualStart))
            
            Write-Host "`n📺 Visual Resources Section:" -ForegroundColor Cyan
            Write-Host "-" * 60
            Write-Host $visualSection
            Write-Host "-" * 60
            
            # Count images and videos
            $imageCount = ([regex]::Matches($visualSection, '🖼️')).Count
            $videoCount = ([regex]::Matches($visualSection, '🎬')).Count
            
            Write-Host "`n[STATS] Statistics:" -ForegroundColor Yellow
            Write-Host "   🖼️  Images section: $imageCount"
            Write-Host "   🎬  Videos section: $videoCount"
            
            if ($imageCount -gt 0 -and $videoCount -gt 0) {
                Write-Host "`n[OK] SUCCESS! Visual resources are working correctly!" -ForegroundColor Green
            } else {
                Write-Host "`n[WARNING]  Warning: Missing image or video sections" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "[ERROR] Visual resources section NOT found!" -ForegroundColor Red
    }
    
} catch {
    Write-Host "[ERROR] Query failed: $_" -ForegroundColor Red
    Write-Host $_.Exception.Message
}

Write-Host "`n" + ("=" * 60)
Write-Host "🏁 Test Complete!" -ForegroundColor Cyan
