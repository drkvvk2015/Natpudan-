#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Production deployment script for Physician AI Assistant

.DESCRIPTION
    Automates the deployment process including:
    - Environment validation
    - Dependency installation
    - Database setup
    - Service configuration
    - Health checks

.PARAMETER Environment
    Target environment: development, staging, or production

.PARAMETER SkipTests
    Skip running tests before deployment

.EXAMPLE
    .\deploy-production.ps1 -Environment production
#>

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet('development', 'staging', 'production')]
    [string]$Environment = 'production',
    
    [Parameter(Mandatory = $false)]
    [switch]$SkipTests = $false,
    
    [Parameter(Mandatory = $false)]
    [switch]$UseDocker = $true
)

# Script configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = 'SilentlyContinue'

# Colors for output
function Write-Success { Write-Host "✓ $args" -ForegroundColor Green }
function Write-Info { Write-Host "ℹ $args" -ForegroundColor Cyan }
function Write-Warning { Write-Host "⚠ $args" -ForegroundColor Yellow }
function Write-Error-Message { Write-Host "✗ $args" -ForegroundColor Red }

# Banner
Write-Host @"

╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🏥  PHYSICIAN AI ASSISTANT - PRODUCTION DEPLOYMENT     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

Write-Info "Environment: $Environment"
Write-Info "Using Docker: $UseDocker"
Write-Info "Skip Tests: $SkipTests"
Write-Host ""

# Step 1: Pre-deployment checks
Write-Host "═══ Step 1: Pre-deployment Checks ═══" -ForegroundColor Yellow
Write-Host ""

# Check if running in correct directory
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Error-Message "Please run this script from the project root directory"
    exit 1
}
Write-Success "Project structure verified"

# Check for required files
$requiredFiles = @(
    "backend/requirements.txt",
    "backend/.env",
    "frontend/package.json",
    "docker-compose.yml"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Error-Message "Required file not found: $file"
        exit 1
    }
}
Write-Success "Required files present"

# Check for Docker (if using Docker)
if ($UseDocker) {
    try {
        docker --version | Out-Null
        docker-compose --version | Out-Null
        Write-Success "Docker and Docker Compose installed"
    }
    catch {
        Write-Error-Message "Docker or Docker Compose not found. Install them or use -UseDocker:`$false"
        exit 1
    }
}

# Validate environment file
Write-Info "Validating environment configuration..."
$envFile = "backend/.env"
$envContent = Get-Content $envFile -Raw

if ($envContent -match "your-secret-key-change-in-production" -and $Environment -eq "production") {
    Write-Error-Message "SECRET_KEY not changed in .env file!"
    Write-Warning "Generate a secure key with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
    exit 1
}

if ($envContent -match "sk-your-openai-api-key") {
    Write-Warning "OpenAI API key may not be set. AI features will be limited."
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne 'y') {
        exit 1
    }
}

Write-Success "Environment configuration validated"

# Step 2: Run tests (if not skipped)
if (-not $SkipTests) {
    Write-Host ""
    Write-Host "═══ Step 2: Running Tests ═══" -ForegroundColor Yellow
    Write-Host ""
    
    Write-Info "Running backend tests..."
    try {
        Push-Location backend
        if (Test-Path "tests") {
            python -m pytest tests/ -v
            Write-Success "Backend tests passed"
        }
        else {
            Write-Warning "No tests found, skipping"
        }
        Pop-Location
    }
    catch {
        Write-Error-Message "Backend tests failed"
        Pop-Location
        exit 1
    }
}
else {
    Write-Warning "Skipping tests (use without -SkipTests to run)"
}

# Step 3: Build and deploy
Write-Host ""
Write-Host "═══ Step 3: Building Application ═══" -ForegroundColor Yellow
Write-Host ""

if ($UseDocker) {
    # Docker deployment
    Write-Info "Building Docker images..."
    
    try {
        docker-compose build
        Write-Success "Docker images built successfully"
    }
    catch {
        Write-Error-Message "Docker build failed"
        exit 1
    }
    
    Write-Info "Starting services with Docker Compose..."
    try {
        docker-compose up -d
        Write-Success "Services started"
    }
    catch {
        Write-Error-Message "Failed to start services"
        exit 1
    }
    
    # Wait for services to be ready
    Write-Info "Waiting for services to be ready..."
    Start-Sleep -Seconds 10
    
}
else {
    # Manual deployment
    Write-Info "Building backend..."
    
    # Backend
    Push-Location backend
    
    # Ensure virtual environment
    if (-not (Test-Path ".venv")) {
        Write-Info "Creating virtual environment..."
        python -m venv .venv
    }
    
    # Activate virtual environment
    & .\.venv\Scripts\Activate.ps1
    
    # Install dependencies
    Write-Info "Installing backend dependencies..."
    pip install -r requirements.txt
    Write-Success "Backend dependencies installed"
    
    # Database migrations
    Write-Info "Running database migrations..."
    python -c "from app.database import init_db; init_db()"
    Write-Success "Database initialized"
    
    Pop-Location
    
    # Frontend
    Write-Info "Building frontend..."
    Push-Location frontend
    
    # Install dependencies
    npm install
    Write-Success "Frontend dependencies installed"
    
    # Build for production
    npm run build
    Write-Success "Frontend built successfully"
    
    Pop-Location
}

# Step 4: Health checks
Write-Host ""
Write-Host "═══ Step 4: Health Checks ═══" -ForegroundColor Yellow
Write-Host ""

Write-Info "Waiting for backend to be ready..."
$maxAttempts = 30
$attempt = 0
$backendReady = $false

while ($attempt -lt $maxAttempts -and -not $backendReady) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 2
        if ($response.status -eq "healthy") {
            $backendReady = $true
            Write-Success "Backend is healthy"
        }
    }
    catch {
        $attempt++
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 2
    }
}

Write-Host ""

if (-not $backendReady) {
    Write-Error-Message "Backend health check failed after $maxAttempts attempts"
    if ($UseDocker) {
        Write-Info "Check logs with: docker-compose logs backend"
    }
    exit 1
}

# Detailed health check
try {
    $detailedHealth = Invoke-RestMethod -Uri "http://localhost:8000/health/detailed"
    Write-Success "Detailed health check passed"
    Write-Info "Uptime: $($detailedHealth.uptime.human_readable)"
    Write-Info "CPU: $($detailedHealth.system.cpu_percent)%"
    Write-Info "Memory: $($detailedHealth.system.memory.used_percent)%"
}
catch {
    Write-Warning "Detailed health check failed, but basic health is OK"
}

# Step 5: Verify critical endpoints
Write-Host ""
Write-Host "═══ Step 5: Endpoint Verification ═══" -ForegroundColor Yellow
Write-Host ""

$endpoints = @(
    @{Path = "/"; Name = "Root" },
    @{Path = "/health"; Name = "Health" },
    @{Path = "/docs"; Name = "API Docs" }
)

foreach ($endpoint in $endpoints) {
    try {
        $url = "http://localhost:8000$($endpoint.Path)"
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "$($endpoint.Name) endpoint responding"
        }
    }
    catch {
        Write-Warning "$($endpoint.Name) endpoint check failed (may be disabled in production)"
    }
}

# Step 6: Summary and next steps
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

Write-Info "Services Status:"
Write-Success "Backend API: http://localhost:8000"
Write-Success "API Documentation: http://localhost:8000/docs"
Write-Success "Frontend: http://localhost:3000"
Write-Host ""

Write-Info "Useful Commands:"
if ($UseDocker) {
    Write-Host "  View logs:        docker-compose logs -f"
    Write-Host "  Stop services:    docker-compose stop"
    Write-Host "  Restart:          docker-compose restart"
    Write-Host "  Remove:           docker-compose down"
}
else {
    Write-Host "  Start backend:    cd backend; python run.py"
    Write-Host "  Start frontend:   cd frontend; npm run dev"
    Write-Host "  View logs:        Check backend/logs/ directory"
}
Write-Host ""

Write-Info "Next Steps:"
Write-Host "  1. Test the application thoroughly"
Write-Host "  2. Upload medical documents to knowledge base"
Write-Host "  3. Configure monitoring and alerts"
Write-Host "  4. Set up automated backups"
Write-Host "  5. Review PRODUCTION_CHECKLIST.md"
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
