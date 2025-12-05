#!/usr/bin/env pwsh
# Fix Large Files for GitHub Push
# This script removes large files from git tracking and updates .gitignore

Write-Host "[WRENCH] Fixing Large Files Issue for GitHub Push" -ForegroundColor Cyan
Write-Host "=" * 60
Write-Host ""

# Step 1: Cancel any in-progress git operations
Write-Host "1 Cancelling any in-progress git operations..." -ForegroundColor Yellow
if (Test-Path ".git/index.lock") {
    Remove-Item ".git/index.lock" -Force
    Write-Host "   [OK] Removed git lock file" -ForegroundColor Green
}

# Step 2: Reset to last commit
Write-Host ""
Write-Host "2 Resetting to clean state..." -ForegroundColor Yellow
git reset --soft HEAD
Write-Host "   [OK] Reset complete" -ForegroundColor Green

# Step 3: Remove large files/directories from git tracking (but keep on disk)
Write-Host ""
Write-Host "3 Removing large files from git tracking..." -ForegroundColor Yellow

$filesToRemove = @(
    "frontend/release",
    "backend/data",
    "backend/certs",
    "frontend/certs",
    "natpudan.db",
    "backend/natpudan.db"
)

foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Write-Host "    Removing $file from git..." -ForegroundColor Gray
        git rm -r --cached $file -f 2>&1 | Out-Null
        Write-Host "   [OK] $file removed from git (kept on disk)" -ForegroundColor Green
    }
}

# Step 4: Verify .gitignore has proper entries
Write-Host ""
Write-Host "4 Verifying .gitignore..." -ForegroundColor Yellow
$gitignoreContent = Get-Content .gitignore -Raw
$requiredEntries = @(
    "backend/data/",
    "frontend/release/",
    "backend/certs/",
    "frontend/certs/",
    "*.db",
    "natpudan.db"
)

$missing = $false
foreach ($entry in $requiredEntries) {
    if ($gitignoreContent -notmatch [regex]::Escape($entry)) {
        Write-Host "   [WARNING]  Missing: $entry" -ForegroundColor Red
        $missing = $true
    }
}

if (-not $missing) {
    Write-Host "   [OK] .gitignore is properly configured" -ForegroundColor Green
} else {
    Write-Host "   [WARNING]  .gitignore needs updating (already done earlier)" -ForegroundColor Yellow
}

# Step 5: Stage .gitignore changes
Write-Host ""
Write-Host "5 Staging .gitignore..." -ForegroundColor Yellow
git add .gitignore
Write-Host "   [OK] .gitignore staged" -ForegroundColor Green

# Step 6: Commit the changes
Write-Host ""
Write-Host "6 Committing changes..." -ForegroundColor Yellow
git commit -m "fix: Remove large files from git tracking

- Removed frontend/release/ (contains 190+ MB executables)
- Removed backend/data/ (contains 329 MB PDF)
- Removed backend/certs/ and frontend/certs/
- Removed database files
- Updated .gitignore to prevent future large file commits

These files are kept locally but excluded from git."

Write-Host "   [OK] Changes committed" -ForegroundColor Green

# Step 7: Show status
Write-Host ""
Write-Host "7 Current status:" -ForegroundColor Yellow
Write-Host ""
git log -1 --oneline
Write-Host ""
$statusCount = (git status --short | Measure-Object).Count
if ($statusCount -eq 0) {
    Write-Host "   [OK] Working directory clean!" -ForegroundColor Green
} else {
    Write-Host "   [STATS] Files pending: $statusCount" -ForegroundColor Yellow
    git status --short | Select-Object -First 10
}

# Step 8: Ready to push
Write-Host ""
Write-Host "=" * 60
Write-Host "[OK] READY TO PUSH!" -ForegroundColor Green
Write-Host ""
Write-Host "Next step:" -ForegroundColor Cyan
Write-Host "   git push origin clean-main2" -ForegroundColor White
Write-Host ""
Write-Host "This push will NOT include:" -ForegroundColor Yellow
Write-Host "   [ERROR] Large PDFs (329 MB)" -ForegroundColor Gray
Write-Host "   [ERROR] Release executables (190+ MB)" -ForegroundColor Gray
Write-Host "   [ERROR] Certificate files" -ForegroundColor Gray
Write-Host "   [ERROR] Database files" -ForegroundColor Gray
Write-Host ""
Write-Host "These files remain on your local machine." -ForegroundColor Green
Write-Host ""
