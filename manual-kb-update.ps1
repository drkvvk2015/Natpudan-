# Manual Knowledge Base Update Script
# Use this when Celery is not available

$ApiUrl = "http://127.0.0.1:8000/api/medical/knowledge/pubmed-auto-update"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   Manual Knowledge Base Update" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "[INFO] Updating knowledge base with latest research..." -ForegroundColor Yellow

$body = @{
    topics = @(
        "diabetes mellitus",
        "hypertension",
        "heart disease",
        "cancer",
        "pneumonia",
        "COVID-19",
        "depression",
        "arthritis"
    )
    papers_per_topic = 5
    days_back = 7
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri $ApiUrl -Method POST -Body $body -ContentType "application/json"
    
    Write-Host "`n[SUCCESS] Knowledge base updated!" -ForegroundColor Green
    Write-Host "Papers indexed: $($response.papers_indexed)" -ForegroundColor Cyan
    Write-Host "Topics processed: $($response.topics_processed)" -ForegroundColor Cyan
    Write-Host "`n" -ForegroundColor Gray
    
    $response | ConvertTo-Json -Depth 5
    
} catch {
    Write-Host "`n[ERROR] Failed to update knowledge base: $_" -ForegroundColor Red
}

Write-Host "`n" -ForegroundColor Gray
