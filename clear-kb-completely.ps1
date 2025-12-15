#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Complete knowledge base wipe - removes ALL data, files, and indices
.DESCRIPTION
    This script performs a complete KB reset by:
    - Stopping backend to avoid file locks
    - Deleting all medical books/PDFs
    - Deleting FAISS index
    - Deleting embeddings cache
    - Clearing database records
    - Restarting backend with empty KB
#>

Write-Host ""
Write-Host "========================================" -ForegroundColor Red
Write-Host " COMPLETE KNOWLEDGE BASE WIPE" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

Write-Host "This will PERMANENTLY delete:" -ForegroundColor Yellow
Write-Host "  ✗ All medical books (74 files, 2.46 GB)" -ForegroundColor White
Write-Host "  ✗ All FAISS indices" -ForegroundColor White
Write-Host "  ✗ All embeddings cache" -ForegroundColor White
Write-Host "  ✗ All database records" -ForegroundColor White
Write-Host ""

$response = Read-Host "Type 'DELETE ALL' to confirm (case-sensitive)"
if ($response -ne "DELETE ALL") {
    Write-Host "Cancelled" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "[1/5] Stopping backend..." -ForegroundColor Cyan

# Find and stop backend process
$backendProcs = Get-Process -Name "python","uvicorn" -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*uvicorn*" -or $_.CommandLine -like "*main.py*"
}

if ($backendProcs) {
    $backendProcs | Stop-Process -Force
    Start-Sleep -Seconds 2
    Write-Host "  ✓ Backend stopped" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Backend not running" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[2/5] Deleting medical books..." -ForegroundColor Cyan

$booksDir = "backend\data\medical_books"
if (Test-Path $booksDir) {
    $fileCount = (Get-ChildItem $booksDir -File -Recurse).Count
    Remove-Item $booksDir -Recurse -Force
    Write-Host "  ✓ Deleted $fileCount files" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Directory not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[3/5] Deleting FAISS index..." -ForegroundColor Cyan

$faissDir = "backend\data\knowledge_base"
if (Test-Path $faissDir) {
    Remove-Item $faissDir -Recurse -Force
    Write-Host "  ✓ FAISS index deleted" -ForegroundColor Green
} else {
    Write-Host "  ⚠ No FAISS index found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[4/5] Deleting embeddings cache..." -ForegroundColor Cyan

$cacheDir = "backend\cache\online_knowledge"
if (Test-Path $cacheDir) {
    Remove-Item $cacheDir -Recurse -Force
    Write-Host "  ✓ Cache deleted" -ForegroundColor Green
} else {
    Write-Host "  ⚠ No cache found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[5/5] Clearing database records..." -ForegroundColor Cyan

# Run Python script to clear DB
$clearScript = @"
import sys
sys.path.insert(0, 'backend')
from app.database import get_db, engine
from app.models import KnowledgeDocument

db = next(get_db())
try:
    count = db.query(KnowledgeDocument).count()
    db.query(KnowledgeDocument).delete()
    db.commit()
    print(f'  ✓ Cleared {count} database records')
except Exception as e:
    print(f'  ✗ Database error: {e}')
    db.rollback()
finally:
    db.close()
"@

$clearScript | python -c "exec(input())"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " KNOWLEDGE BASE WIPED" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "All data deleted. KB is now completely empty." -ForegroundColor Green
Write-Host ""
Write-Host "To restart backend with empty KB:" -ForegroundColor Cyan
Write-Host "  .\start-backend.ps1" -ForegroundColor White
Write-Host ""
