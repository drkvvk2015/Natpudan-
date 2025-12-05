Param(
    [string]$ApiUrl = "http://127.0.0.1:8000"
)

try {
    $resp = Invoke-RestMethod -Uri "$ApiUrl/api/error-correction/errors/clear" -Method Post -TimeoutSec 5
    Write-Host "Cleared errors: $($resp.message)" -ForegroundColor Green
} catch {
    Write-Error "Failed to clear errors: $_"
}
