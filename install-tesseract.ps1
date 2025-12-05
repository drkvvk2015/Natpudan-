# Tesseract OCR Installation Guide for Windows

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "  Tesseract OCR Setup" -ForegroundColor Cyan  
Write-Host "================================`n" -ForegroundColor Cyan

# Check if Tesseract is already installed
$tesseractPath = "C:\Program Files\Tesseract-OCR\tesseract.exe"

if (Test-Path $tesseractPath) {
    Write-Host "[OK] Tesseract is already installed!" -ForegroundColor Green
    & $tesseractPath --version
    Write-Host "`nTesseract is ready to use." -ForegroundColor Green
    
    # Check if it's in PATH
    try {
        $version = tesseract --version 2>&1 | Select-String "tesseract"
        Write-Host "[OK] Tesseract is in PATH" -ForegroundColor Green
    } catch {
        Write-Host "`n[WARNING] Tesseract is installed but not in PATH" -ForegroundColor Yellow
        Write-Host "Adding to PATH..." -ForegroundColor Yellow
        $env:Path += ";C:\Program Files\Tesseract-OCR"
        Write-Host "[OK] Added to PATH for this session" -ForegroundColor Green
        Write-Host "`nTo make permanent, run this as Administrator:" -ForegroundColor Yellow
        Write-Host '[Environment]::SetEnvironmentVariable("Path", $env:Path, [EnvironmentVariableTarget]::Machine)' -ForegroundColor White
    }
    
    exit 0
}

Write-Host "[INFO] Tesseract OCR is not installed" -ForegroundColor Yellow
Write-Host "`nTesseract enables OCR (Optical Character Recognition) for scanned PDFs." -ForegroundColor White
Write-Host "Without it, image-based PDFs cannot be processed.`n" -ForegroundColor White

# Installation options
Write-Host "Installation Options:" -ForegroundColor Cyan
Write-Host "1. Download manually (recommended)" -ForegroundColor White
Write-Host "2. Install via Chocolatey (if available)" -ForegroundColor White
Write-Host "3. Skip for now (text-only PDFs will work)" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter choice (1-3)"

switch ($choice) {
    "1" {
        Write-Host "`n[MANUAL INSTALL]" -ForegroundColor Cyan
        Write-Host "Opening download page..." -ForegroundColor White
        Start-Process "https://github.com/UB-Mannheim/tesseract/wiki"
        
        Write-Host "`nSteps:" -ForegroundColor Cyan
        Write-Host "1. Download: tesseract-ocr-w64-setup-5.3.3.*.exe" -ForegroundColor White
        Write-Host "2. Run installer" -ForegroundColor White
        Write-Host "3. Install to: C:\Program Files\Tesseract-OCR (default)" -ForegroundColor White
        Write-Host "4. Run this script again to verify" -ForegroundColor White
        
        Write-Host "`nPress any key after installation..." -ForegroundColor Yellow
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        
        # Check again
        if (Test-Path $tesseractPath) {
            Write-Host "`n[OK] Tesseract detected!" -ForegroundColor Green
            & $tesseractPath --version
            
            # Add to PATH
            $env:Path += ";C:\Program Files\Tesseract-OCR"
            Write-Host "`n[OK] Added to PATH for this session" -ForegroundColor Green
            
            Write-Host "`nTo make PATH permanent (run as Administrator):" -ForegroundColor Yellow
            Write-Host '[Environment]::SetEnvironmentVariable("Path", $env:Path, [EnvironmentVariableTarget]::Machine)' -ForegroundColor White
        } else {
            Write-Host "`n[ERROR] Tesseract not found. Please complete installation." -ForegroundColor Red
        }
    }
    
    "2" {
        Write-Host "`n[CHOCOLATEY INSTALL]" -ForegroundColor Cyan
        
        # Check if Chocolatey is installed
        try {
            $chocoVersion = choco --version
            Write-Host "[OK] Chocolatey is installed: $chocoVersion" -ForegroundColor Green
            
            Write-Host "`nInstalling Tesseract OCR..." -ForegroundColor White
            choco install tesseract -y
            
            if (Test-Path $tesseractPath) {
                Write-Host "`n[OK] Tesseract installed successfully!" -ForegroundColor Green
                & $tesseractPath --version
                
                # Add to PATH
                $env:Path += ";C:\Program Files\Tesseract-OCR"
                Write-Host "`n[OK] Added to PATH" -ForegroundColor Green
            } else {
                Write-Host "`n[ERROR] Installation failed" -ForegroundColor Red
            }
        } catch {
            Write-Host "[ERROR] Chocolatey is not installed" -ForegroundColor Red
            Write-Host "Install Chocolatey from: https://chocolatey.org/install" -ForegroundColor Yellow
            Write-Host "Then run this script again" -ForegroundColor Yellow
        }
    }
    
    "3" {
        Write-Host "`n[SKIPPED]" -ForegroundColor Yellow
        Write-Host "OCR will not be available. Only text-based PDFs can be processed." -ForegroundColor Yellow
        Write-Host "You can install Tesseract later and run this script again." -ForegroundColor White
    }
    
    default {
        Write-Host "`nInvalid choice. Exiting." -ForegroundColor Red
    }
}

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "  Next Steps" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

if (Test-Path $tesseractPath) {
    Write-Host "1. Restart your backend server" -ForegroundColor White
    Write-Host "2. Test OCR status:" -ForegroundColor White
    Write-Host "   curl http://127.0.0.1:8000/api/medical/knowledge/ocr-status" -ForegroundColor Gray
    Write-Host "3. Upload scanned PDFs - OCR will be applied automatically" -ForegroundColor White
} else {
    Write-Host "1. Complete Tesseract installation" -ForegroundColor White
    Write-Host "2. Run this script again to verify" -ForegroundColor White
    Write-Host "3. Restart backend server" -ForegroundColor White
}

Write-Host ""
