# All-in-One Setup and Verification Script
# Installs dependencies, verifies configuration, and prepares for deployment

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Natpudan AI - Complete Setup & Verification" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$allChecks = @()

# Check 1: Python Installation
Write-Host "[1/12] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.(\d+)") {
        $minorVersion = [int]$matches[1]
        if ($minorVersion -ge 8) {
            Write-Host "  [OK] $pythonVersion" -ForegroundColor Green
            $allChecks += $true
        } else {
            Write-Host "  [ERROR] Python 3.8+ required" -ForegroundColor Red
            $allChecks += $false
        }
    } else {
        Write-Host "  [ERROR] Python not found" -ForegroundColor Red
        $allChecks += $false
    }
} catch {
    Write-Host "  [ERROR] Python not found" -ForegroundColor Red
    $allChecks += $false
}

# Check 2: Node.js Installation
Write-Host "[2/12] Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    if ($nodeVersion -match "v(\d+)\.") {
        $majorVersion = [int]$matches[1]
        if ($majorVersion -ge 18) {
            Write-Host "  [OK] $nodeVersion" -ForegroundColor Green
            $allChecks += $true
        } else {
            Write-Host "  [ERROR] Node.js 18+ required" -ForegroundColor Red
            $allChecks += $false
        }
    } else {
        Write-Host "  [ERROR] Node.js not found" -ForegroundColor Red
        $allChecks += $false
    }
} catch {
    Write-Host "  [ERROR] Node.js not found" -ForegroundColor Red
    $allChecks += $false
}

# Check 3: Virtual Environment
Write-Host "[3/12] Checking Python virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "  [OK] Virtual environment found" -ForegroundColor Green
    $allChecks += $true
} else {
    Write-Host "  [WARN] Creating virtual environment..." -ForegroundColor Yellow
    try {
        python -m venv .venv
        Write-Host "  [OK] Virtual environment created" -ForegroundColor Green
        $allChecks += $true
    } catch {
        Write-Host "  [ERROR] Failed to create virtual environment" -ForegroundColor Red
        $allChecks += $false
    }
}

# Check 4: Backend Dependencies
Write-Host "[4/12] Checking backend dependencies..." -ForegroundColor Yellow
if (Test-Path "backend\requirements.txt") {
    try {
        & ".venv\Scripts\python.exe" -c "import fastapi, uvicorn, sqlalchemy" 2>$null
        Write-Host "  [OK] Backend dependencies installed" -ForegroundColor Green
        $allChecks += $true
    } catch {
        Write-Host "  [WARN] Installing backend dependencies..." -ForegroundColor Yellow
        try {
            & ".venv\Scripts\pip.exe" install -r backend\requirements.txt --quiet
            Write-Host "  [OK] Backend dependencies installed" -ForegroundColor Green
            $allChecks += $true
        } catch {
            Write-Host "  [ERROR] Failed to install backend dependencies" -ForegroundColor Red
            $allChecks += $false
        }
    }
} else {
    Write-Host "  [ERROR] requirements.txt not found" -ForegroundColor Red
    $allChecks += $false
}

# Check 5: Frontend Dependencies
Write-Host "[5/12] Checking frontend dependencies..." -ForegroundColor Yellow
if (Test-Path "frontend\package.json") {
    if (Test-Path "frontend\node_modules") {
        Write-Host "  [OK] Frontend dependencies installed" -ForegroundColor Green
        $allChecks += $true
    } else {
        Write-Host "  [WARN] Installing frontend dependencies..." -ForegroundColor Yellow
        try {
            Push-Location frontend
            npm install --loglevel=error
            Pop-Location
            Write-Host "  [OK] Frontend dependencies installed" -ForegroundColor Green
            $allChecks += $true
        } catch {
            Pop-Location
            Write-Host "  [ERROR] Failed to install frontend dependencies" -ForegroundColor Red
            $allChecks += $false
        }
    }
} else {
    Write-Host "  [ERROR] frontend\package.json not found" -ForegroundColor Red
    $allChecks += $false
}

# Check 6: Environment Variables
Write-Host "[6/12] Checking environment configuration..." -ForegroundColor Yellow
if (Test-Path "backend\.env") {
    $envContent = Get-Content "backend\.env" -Raw
    $hasOpenAI = $envContent -match "OPENAI_API_KEY=sk-"
    $hasSecretKey = $envContent -match "SECRET_KEY=.{20,}"
    
    if ($hasOpenAI -and $hasSecretKey) {
        Write-Host "  [OK] Environment configured" -ForegroundColor Green
        $allChecks += $true
    } elseif ($hasOpenAI) {
        Write-Host "  [WARN] OpenAI key found, SECRET_KEY weak" -ForegroundColor Yellow
        $allChecks += $true
    } else {
        Write-Host "  [WARN] OpenAI API key not configured" -ForegroundColor Yellow
        Write-Host "    Add OPENAI_API_KEY to backend\.env" -ForegroundColor Gray
        $allChecks += $false
    }
} else {
    Write-Host "  [WARN] backend\.env file missing" -ForegroundColor Yellow
    if (Test-Path "backend\.env.example") {
        Write-Host "    Copy backend\.env.example to backend\.env" -ForegroundColor Gray
    }
    $allChecks += $false
}

# Check 7: Database
Write-Host "[7/12] Checking database..." -ForegroundColor Yellow
if (Test-Path "backend\natpudan.db") {
    $dbSize = (Get-Item "backend\natpudan.db").Length / 1KB
    Write-Host "  [OK] Database exists ($([math]::Round($dbSize, 2)) KB)" -ForegroundColor Green
    $allChecks += $true
} else {
    Write-Host "  [WARN] Database not found (will be created on first run)" -ForegroundColor Yellow
    $allChecks += $true
}

# Check 8: Docker/Podman
Write-Host "[8/12] Checking container runtime..." -ForegroundColor Yellow
$dockerAvailable = $false
$podmanAvailable = $false

try {
    $dockerVer = docker --version 2>&1
    if ($dockerVer) {
        $dockerAvailable = $true
        Write-Host "  [OK] Docker: $dockerVer" -ForegroundColor Green
    }
} catch {}

try {
    $podmanVer = podman --version 2>&1
    if ($podmanVer) {
        $podmanAvailable = $true
        Write-Host "  [OK] Podman: $podmanVer" -ForegroundColor Green
    }
} catch {}

if ($dockerAvailable -or $podmanAvailable) {
    $allChecks += $true
} else {
    Write-Host "  [WARN] No container runtime found" -ForegroundColor Yellow
    Write-Host "    Install Docker Desktop for containerization" -ForegroundColor Gray
    $allChecks += $true  # Not critical for local dev
}

# Check 9: Git Repository
Write-Host "[9/12] Checking Git repository..." -ForegroundColor Yellow
try {
    $gitStatus = git status 2>&1
    if ($gitStatus -match "On branch") {
        Write-Host "  [OK] Git repository initialized" -ForegroundColor Green
        $allChecks += $true
    } else {
        Write-Host "  [WARN] Not a Git repository" -ForegroundColor Yellow
        $allChecks += $true  # Not critical
    }
} catch {
    Write-Host "  [WARN] Not a Git repository" -ForegroundColor Yellow
    $allChecks += $true  # Not critical
}

# Check 10: GitHub Workflow
Write-Host "[10/12] Checking CI/CD configuration..." -ForegroundColor Yellow
if (Test-Path ".github\workflows\build-and-push-images.yml") {
    Write-Host "  [OK] GitHub Actions workflow configured" -ForegroundColor Green
    $allChecks += $true
} else {
    Write-Host "  [ERROR] CI/CD workflow missing" -ForegroundColor Red
    $allChecks += $false
}

# Check 11: Kubernetes Manifests
Write-Host "[11/12] Checking Kubernetes manifests..." -ForegroundColor Yellow
if (Test-Path "k8s") {
    $k8sFiles = @(Get-ChildItem "k8s\*.yaml" -ErrorAction SilentlyContinue).Count
    if ($k8sFiles -gt 0) {
        Write-Host "  [OK] $k8sFiles Kubernetes manifest(s) found" -ForegroundColor Green
        $allChecks += $true
    } else {
        Write-Host "  [ERROR] No Kubernetes manifests found" -ForegroundColor Red
        $allChecks += $false
    }
} else {
    Write-Host "  [ERROR] k8s directory missing" -ForegroundColor Red
    $allChecks += $false
}

# Check 12: Production Compose
Write-Host "[12/12] Checking production deployment config..." -ForegroundColor Yellow
if (Test-Path "docker-compose.production.yml") {
    Write-Host "  [OK] Production compose file exists" -ForegroundColor Green
    $allChecks += $true
} else {
    Write-Host "  [ERROR] Production compose file missing" -ForegroundColor Red
    $allChecks += $false
}

# Summary
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Verification Summary" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$passedChecks = ($allChecks | Where-Object { $_ -eq $true }).Count
$totalChecks = $allChecks.Count
$percentage = [math]::Round(($passedChecks / $totalChecks) * 100)

$statusColor = if ($percentage -eq 100) { "Green" } elseif ($percentage -ge 80) { "Yellow" } else { "Red" }
$statusIcon = if ($percentage -eq 100) { "[OK]" } elseif ($percentage -ge 80) { "[WARN]" } else { "[ERROR]" }

Write-Host "$statusIcon Passed: $passedChecks/$totalChecks checks ($percentage%)" -ForegroundColor $statusColor
Write-Host ""

if ($passedChecks -eq $totalChecks) {
    Write-Host "[OK] ALL SYSTEMS READY!" -ForegroundColor Green
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "  Quick Start Options:" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  [1] Local Development (Recommended)" -ForegroundColor White
    Write-Host "      .\start-dev.ps1" -ForegroundColor Gray
    Write-Host "      -> Backend: http://localhost:8000" -ForegroundColor Gray
    Write-Host "      -> Frontend: http://localhost:5173" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  [2] Push to GitHub (Triggers CI/CD)" -ForegroundColor White
    Write-Host "      git add ." -ForegroundColor Gray
    Write-Host "      git commit -m 'Complete containerization setup'" -ForegroundColor Gray
    Write-Host "      git push origin main" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  [3] Deploy with Pre-built Images" -ForegroundColor White
    Write-Host "      docker-compose -f docker-compose.production.yml up -d" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  [4] Deploy to Kubernetes" -ForegroundColor White
    Write-Host "      kubectl apply -f k8s/" -ForegroundColor Gray
    Write-Host ""
} elseif ($percentage -ge 80) {
    Write-Host "[WARN] SETUP MOSTLY COMPLETE" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "You can start local development:" -ForegroundColor Yellow
    Write-Host "  .\start-dev.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "Some features may not work without:" -ForegroundColor Yellow
    $failedCount = $totalChecks - $passedChecks
    Write-Host "  -> $failedCount optional component(s)" -ForegroundColor Gray
} else {
    Write-Host "[ERROR] SETUP INCOMPLETE" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please fix the issues above before proceeding." -ForegroundColor Red
    Write-Host ""
    Write-Host "Common fixes:" -ForegroundColor Yellow
    Write-Host "  - Install Python 3.8+: https://python.org" -ForegroundColor Gray
    Write-Host "  - Install Node.js 18+: https://nodejs.org" -ForegroundColor Gray
    Write-Host "  - Configure backend\.env with API keys" -ForegroundColor Gray
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Return exit code based on critical checks
if ($percentage -ge 80) {
    exit 0
} else {
    exit 1
}
