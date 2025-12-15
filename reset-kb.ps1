# Reset Knowledge Base - Clears all cached data
param([switch]$Help)

if ($Help) {
    Write-Host "Reset Knowledge Base - Clears all indexed documents and cache" -ForegroundColor Cyan
    Write-Host "Usage: .\reset-kb.ps1" -ForegroundColor Yellow
    exit 0
}

Write-Host "" -ForegroundColor Cyan
Write-Host "=== RESETTING KNOWLEDGE BASE ===" -ForegroundColor Cyan

# Stop services
Write-Host "Stopping services..." -ForegroundColor Yellow
docker-compose down 2>$null

# Clear knowledge base
Write-Host "Clearing knowledge base files..." -ForegroundColor Yellow
$kbPath = "D:\Users\CNSHO\Documents\GitHub\Natpudan-\backend\data\knowledge_base"
if (Test-Path $kbPath) {
    Remove-Item "$kbPath\*" -Force -Recurse 2>$null
    Write-Host "  OK - Knowledge base cleared" -ForegroundColor Green
}

# Clear cache
Write-Host "Clearing cache..." -ForegroundColor Yellow
$cachePath = "D:\Users\CNSHO\Documents\GitHub\Natpudan-\backend\cache"
if (Test-Path $cachePath) {
    Remove-Item "$cachePath\*" -Force -Recurse 2>$null
    Write-Host "  OK - Cache cleared" -ForegroundColor Green
}

# Clear database
Write-Host "Clearing database..." -ForegroundColor Yellow
$dbPath = "D:\Users\CNSHO\Documents\GitHub\Natpudan-\backend\natpudan.db"
if (Test-Path $dbPath) {
    Remove-Item $dbPath -Force 2>$null
    Write-Host "  OK - Database cleared" -ForegroundColor Green
}

Write-Host "" -ForegroundColor Green
Write-Host "=== RESET COMPLETE ===" -ForegroundColor Green
Write-Host "Run .\start-all.ps1 to restart with clean slate" -ForegroundColor Yellow
Write-Host "" -ForegroundColor Yellow
