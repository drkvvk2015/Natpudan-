#!/usr/bin/env pwsh
# Comprehensive Codebase Cleanup Script
# Removes logs, unwanted files, and organizes for production

Write-Host "="*80 -ForegroundColor Cyan
Write-Host " 🧹 COMPREHENSIVE CODEBASE CLEANUP" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Cyan
Write-Host ""

$rootPath = $PSScriptRoot
$totalCleaned = 0
$totalSize = 0

# 1. Remove all log files
Write-Host "1️⃣  Removing Log Files..." -ForegroundColor Yellow
$logPatterns = @(
    "*.log",
    "debug.log",
    "error.log",
    "backend/logs/*.log",
    "frontend/logs/*.log"
)

foreach ($pattern in $logPatterns) {
    $logFiles = Get-ChildItem -Path $rootPath -Filter $pattern -Recurse -ErrorAction SilentlyContinue
    foreach ($file in $logFiles) {
        $size = $file.Length
        Remove-Item $file.FullName -Force
        $totalCleaned++
        $totalSize += $size
        Write-Host "   ✅ Removed: $($file.Name) ($([math]::Round($size/1KB, 2)) KB)" -ForegroundColor Green
    }
}

# Clear backend logs directory but keep the folder
if (Test-Path "$rootPath\backend\logs") {
    Get-ChildItem "$rootPath\backend\logs" -File | Remove-Item -Force
    Write-Host "   ✅ Cleared backend/logs directory" -ForegroundColor Green
}

# 2. Remove backup database files
Write-Host ""
Write-Host "2️⃣  Removing Backup Database Files..." -ForegroundColor Yellow
$backupPatterns = @(
    "*.db.bak",
    "*.db.backup*",
    "*physician_ai.db",
    "backend/*.db.backup*"
)

foreach ($pattern in $backupPatterns) {
    $backupFiles = Get-ChildItem -Path $rootPath -Filter $pattern -Recurse -ErrorAction SilentlyContinue
    foreach ($file in $backupFiles) {
        # Keep the main natpudan.db
        if ($file.Name -ne "natpudan.db") {
            $size = $file.Length
            Remove-Item $file.FullName -Force
            $totalCleaned++
            $totalSize += $size
            Write-Host "   ✅ Removed: $($file.Name) ($([math]::Round($size/1MB, 2)) MB)" -ForegroundColor Green
        }
    }
}

# 3. Remove Python cache files
Write-Host ""
Write-Host "3️⃣  Removing Python Cache Files..." -ForegroundColor Yellow
$cachePatterns = @(
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".pytest_cache"
)

foreach ($pattern in $cachePatterns) {
    if ($pattern -like "*cache*") {
        # Remove directories
        $cacheDirs = Get-ChildItem -Path $rootPath -Filter $pattern -Recurse -Directory -ErrorAction SilentlyContinue
        foreach ($dir in $cacheDirs) {
            $size = (Get-ChildItem $dir.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum
            Remove-Item $dir.FullName -Recurse -Force
            $totalCleaned++
            $totalSize += $size
            Write-Host "   ✅ Removed: $($dir.FullName.Replace($rootPath, '.'))" -ForegroundColor Green
        }
    } else {
        # Remove files
        $cacheFiles = Get-ChildItem -Path $rootPath -Filter $pattern -Recurse -ErrorAction SilentlyContinue
        foreach ($file in $cacheFiles) {
            $size = $file.Length
            Remove-Item $file.FullName -Force
            $totalCleaned++
            $totalSize += $size
        }
    }
}
Write-Host "   ✅ Cleared all Python cache files" -ForegroundColor Green

# 4. Remove duplicate/redundant documentation files
Write-Host ""
Write-Host "4️⃣  Organizing Documentation..." -ForegroundColor Yellow

# Create docs folder if it doesn't exist
$docsPath = "$rootPath\docs"
if (-not (Test-Path $docsPath)) {
    New-Item -Path $docsPath -ItemType Directory | Out-Null
    Write-Host "   ✅ Created docs/ directory" -ForegroundColor Green
}

# Move documentation files to docs folder
$docFiles = Get-ChildItem -Path $rootPath -Filter "*.md" -File | Where-Object { 
    $_.Name -ne "README.md" -and $_.Name -ne "QUICKSTART_GUIDE.md"
}

foreach ($doc in $docFiles) {
    $destPath = "$docsPath\$($doc.Name)"
    if (Test-Path $destPath) {
        Remove-Item $destPath -Force
    }
    Move-Item $doc.FullName $destPath -Force
}
Write-Host "   ✅ Moved $($docFiles.Count) documentation files to docs/" -ForegroundColor Green

# 5. Remove test files from root (keep test scripts in tests folder)
Write-Host ""
Write-Host "5️⃣  Organizing Test Files..." -ForegroundColor Yellow

$testFiles = Get-ChildItem -Path $rootPath -Filter "test*.ps1" -File
$testFiles += Get-ChildItem -Path $rootPath -Filter "test*.py" -File
$testFiles += Get-ChildItem -Path $rootPath -Filter "test*.html" -File
$testFiles += Get-ChildItem -Path $rootPath -Filter "test*.txt" -File

# Create tests folder if needed
$testsPath = "$rootPath\tests"
if (-not (Test-Path $testsPath)) {
    New-Item -Path $testsPath -ItemType Directory | Out-Null
}

foreach ($test in $testFiles) {
    $destPath = "$testsPath\$($test.Name)"
    if (Test-Path $destPath) {
        Remove-Item $destPath -Force
    }
    Move-Item $test.FullName $destPath -Force
}
Write-Host "   ✅ Moved $($testFiles.Count) test files to tests/" -ForegroundColor Green

# 6. Remove duplicate start scripts (keep only essential ones)
Write-Host ""
Write-Host "6️⃣  Cleaning Start Scripts..." -ForegroundColor Yellow

$scriptsToKeep = @(
    "start-backend.ps1",
    "start-frontend.ps1",
    "start-dev.ps1",
    "START-NATPUDAN.ps1"
)

$startScripts = Get-ChildItem -Path $rootPath -Filter "start*.ps1" -File | 
    Where-Object { $scriptsToKeep -notcontains $_.Name }

foreach ($script in $startScripts) {
    Remove-Item $script.FullName -Force
    $totalCleaned++
    Write-Host "   ✅ Removed duplicate: $($script.Name)" -ForegroundColor Green
}

# Remove .bat start files (we use .ps1)
$batFiles = Get-ChildItem -Path $rootPath -Filter "start*.bat" -File
foreach ($bat in $batFiles) {
    Remove-Item $bat.FullName -Force
    $totalCleaned++
    Write-Host "   ✅ Removed: $($bat.Name)" -ForegroundColor Green
}

# 7. Remove uploaded PDFs from root (should be in data/knowledge_base)
Write-Host ""
Write-Host "7️⃣  Organizing PDF Files..." -ForegroundColor Yellow

$pdfFiles = Get-ChildItem -Path $rootPath -Filter "*.pdf" -File
if ($pdfFiles.Count -gt 0) {
    $kbPath = "$rootPath\backend\data\knowledge_base"
    if (-not (Test-Path $kbPath)) {
        New-Item -Path $kbPath -ItemType Directory -Force | Out-Null
    }
    
    foreach ($pdf in $pdfFiles) {
        $destPath = "$kbPath\$($pdf.Name)"
        if (Test-Path $destPath) {
            # File already exists in KB, remove from root
            Remove-Item $pdf.FullName -Force
            Write-Host "   ✅ Removed duplicate: $($pdf.Name)" -ForegroundColor Green
        } else {
            # Move to knowledge base
            Move-Item $pdf.FullName $destPath -Force
            Write-Host "   ✅ Moved to KB: $($pdf.Name)" -ForegroundColor Green
        }
        $totalCleaned++
    }
}

# 8. Clean node_modules if present in root (should only be in frontend)
Write-Host ""
Write-Host "8️⃣  Cleaning Node Modules..." -ForegroundColor Yellow

if (Test-Path "$rootPath\node_modules") {
    Write-Host "   ⚠️  Found node_modules in root (should only be in frontend/)" -ForegroundColor Yellow
    $response = Read-Host "   Remove root node_modules? (y/n)"
    if ($response -eq 'y') {
        Remove-Item "$rootPath\node_modules" -Recurse -Force
        Write-Host "   ✅ Removed root node_modules" -ForegroundColor Green
        $totalCleaned++
    }
}

# 9. Remove backend test/debug files
Write-Host ""
Write-Host "9️⃣  Cleaning Backend Test Files..." -ForegroundColor Yellow

$backendTestFiles = @(
    "ultra_minimal.py",
    "test_auth.py",
    "test_debug.py",
    "test_enhanced_kb.py",
    "test_import.py",
    "test_minimal.py",
    "test_openai.py",
    "test_routers.py",
    "test_startup.py",
    "start_backend_debug.ps1"
)

foreach ($file in $backendTestFiles) {
    $filePath = "$rootPath\backend\$file"
    if (Test-Path $filePath) {
        # Move to backend/tests instead of deleting
        $backendTestsPath = "$rootPath\backend\tests"
        if (-not (Test-Path $backendTestsPath)) {
            New-Item -Path $backendTestsPath -ItemType Directory | Out-Null
        }
        Move-Item $filePath "$backendTestsPath\$file" -Force
        Write-Host "   ✅ Moved to backend/tests: $file" -ForegroundColor Green
    }
}

# 10. Remove duplicate upload scripts
Write-Host ""
Write-Host "🔟 Cleaning Upload Scripts..." -ForegroundColor Yellow

$uploadScriptsToRemove = @(
    "quick-upload.ps1",
    "quick-upload-fixed.ps1",
    "reprocess-uploads.ps1",
    "upload-pdfs-working.ps1",
    "upload-large-pdfs.ps1",
    "upload-medical-pdfs.ps1"
)

foreach ($script in $uploadScriptsToRemove) {
    $scriptPath = "$rootPath\$script"
    if (Test-Path $scriptPath) {
        Remove-Item $scriptPath -Force
        $totalCleaned++
        Write-Host "   ✅ Removed: $script" -ForegroundColor Green
    }
}

# Keep only these essential upload scripts
Write-Host "   ✅ Kept essential scripts: bulk_upload_pdfs.ps1, upload-to-local-kb.ps1" -ForegroundColor Green

# 11. Clean up temporary/duplicate config files
Write-Host ""
Write-Host "1️⃣1️⃣  Cleaning Config Files..." -ForegroundColor Yellow

$configToRemove = @(
    "backend_audit.json",
    ".gitlab-ci.yml",
    "Diagnosis.tsx.bak"
)

foreach ($config in $configToRemove) {
    $configPath = "$rootPath\$config"
    if (Test-Path $configPath) {
        Remove-Item $configPath -Force
        $totalCleaned++
        Write-Host "   ✅ Removed: $config" -ForegroundColor Green
    }
}

# 12. Remove unnecessary backend numbered files
Write-Host ""
Write-Host "1️⃣2️⃣  Cleaning Backend Numbered Files..." -ForegroundColor Yellow

$numberedFiles = @("300", "500", "1000", "1500")
foreach ($file in $numberedFiles) {
    $filePath = "$rootPath\backend\$file"
    if (Test-Path $filePath) {
        Remove-Item $filePath -Force
        $totalCleaned++
        Write-Host "   ✅ Removed: backend/$file" -ForegroundColor Green
    }
}

# 13. Create .gitignore for cleaned items
Write-Host ""
Write-Host "1️⃣3️⃣  Updating .gitignore..." -ForegroundColor Yellow

$gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
.venv311/
venv/
ENV/
env/

# Logs
*.log
logs/
backend/logs/*.log

# Database backups
*.db.bak
*.db.backup*
physician_ai.db

# IDE
.vscode/
.idea/
.vs/

# Node
node_modules/
npm-debug.log*

# OS
.DS_Store
Thumbs.db

# Test files
*.test.js
*.spec.js

# Cache
.pytest_cache/
.cache/

# Environment
.env.local
.env.*.local

# Build outputs
dist/
build/
*.egg-info/

# PDF uploads (managed in backend/data/knowledge_base)
/*.pdf

# Temporary files
*.tmp
*.temp
*.swp
*.swo

# Debug files
debug_*
test_output_*
"@

Set-Content -Path "$rootPath\.gitignore" -Value $gitignoreContent
Write-Host "   ✅ Updated .gitignore with cleanup patterns" -ForegroundColor Green

# 14. Final summary
Write-Host ""
Write-Host "="*80 -ForegroundColor Cyan
Write-Host " ✅ CLEANUP COMPLETE" -ForegroundColor Green
Write-Host "="*80 -ForegroundColor Cyan
Write-Host ""

Write-Host "📊 Cleanup Summary:" -ForegroundColor Yellow
Write-Host "   • Files cleaned: $totalCleaned" -ForegroundColor White
Write-Host "   • Space freed: $([math]::Round($totalSize/1MB, 2)) MB" -ForegroundColor White
Write-Host ""

Write-Host "📁 Organized Structure:" -ForegroundColor Yellow
Write-Host "   ✅ Documentation → docs/" -ForegroundColor Green
Write-Host "   ✅ Test files → tests/" -ForegroundColor Green
Write-Host "   ✅ Backend tests → backend/tests/" -ForegroundColor Green
Write-Host "   ✅ PDF files → backend/data/knowledge_base/" -ForegroundColor Green
Write-Host "   ✅ Logs cleared" -ForegroundColor Green
Write-Host "   ✅ Cache cleared" -ForegroundColor Green
Write-Host "   ✅ Duplicates removed" -ForegroundColor Green
Write-Host ""

Write-Host "🎯 Essential Files Kept:" -ForegroundColor Yellow
Write-Host "   • README.md" -ForegroundColor White
Write-Host "   • QUICKSTART_GUIDE.md" -ForegroundColor White
Write-Host "   • start-backend.ps1" -ForegroundColor White
Write-Host "   • start-frontend.ps1" -ForegroundColor White
Write-Host "   • start-dev.ps1" -ForegroundColor White
Write-Host "   • START-NATPUDAN.ps1" -ForegroundColor White
Write-Host "   • bulk_upload_pdfs.ps1" -ForegroundColor White
Write-Host "   • natpudan.db (main database)" -ForegroundColor White
Write-Host ""

Write-Host "💡 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Review docs/ folder for documentation" -ForegroundColor White
Write-Host "   2. Run tests from tests/ folder if needed" -ForegroundColor White
Write-Host "   3. Use START-NATPUDAN.ps1 to launch the app" -ForegroundColor White
Write-Host "   4. Commit cleaned codebase to git" -ForegroundColor White
Write-Host ""

Write-Host "🚀 Your codebase is now clean and production-ready!" -ForegroundColor Green
Write-Host ""
