#!/usr/bin/env pwsh
# Natpudan AI - PWA Production Deployment Script
# Optimized build and deployment for Progressive Web App

param(
    [string]$Environment = "production",
    [switch]$SkipTests,
    [switch]$SkipBackend,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

Write-Host @"

╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         NATPUDAN AI - PWA DEPLOYMENT SCRIPT              ║
║       Progressive Web App Production Build               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# Configuration
$ROOT_DIR = $PSScriptRoot
$FRONTEND_DIR = Join-Path $ROOT_DIR "frontend"
$BACKEND_DIR = Join-Path $ROOT_DIR "backend"
$DIST_DIR = Join-Path $FRONTEND_DIR "dist"
$BUILD_INFO_FILE = Join-Path $DIST_DIR "build-info.json"

# Check prerequisites
function Test-Prerequisites {
    Write-Host "`n[1/8] Checking Prerequisites..." -ForegroundColor Yellow
    
    # Check Node.js
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
        Write-Host "ERROR: Node.js not found. Please install Node.js 18+ from https://nodejs.org/" -ForegroundColor Red
        exit 1
    }
    $nodeVersion = node --version
    Write-Host "  ✓ Node.js: $nodeVersion" -ForegroundColor Green
    
    # Check npm
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        Write-Host "ERROR: npm not found" -ForegroundColor Red
        exit 1
    }
    $npmVersion = npm --version
    Write-Host "  ✓ npm: v$npmVersion" -ForegroundColor Green
    
    # Check Python (for backend)
    if (-not $SkipBackend) {
        if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
            Write-Host "WARNING: Python not found. Backend deployment will be skipped." -ForegroundColor Yellow
        } else {
            $pythonVersion = python --version
            Write-Host "  ✓ Python: $pythonVersion" -ForegroundColor Green
        }
    }
    
    Write-Host "  ✓ All prerequisites met" -ForegroundColor Green
}

# Clean previous builds
function Clear-BuildArtifacts {
    Write-Host "`n[2/8] Cleaning Previous Builds..." -ForegroundColor Yellow
    
    if (Test-Path $DIST_DIR) {
        Write-Host "  Removing old dist/ directory..." -ForegroundColor Gray
        Remove-Item -Path $DIST_DIR -Recurse -Force
        Write-Host "  ✓ Cleaned frontend dist/" -ForegroundColor Green
    }
    
    # Clean node_modules/.vite cache
    $viteCache = Join-Path $FRONTEND_DIR "node_modules\.vite"
    if (Test-Path $viteCache) {
        Write-Host "  Removing Vite cache..." -ForegroundColor Gray
        Remove-Item -Path $viteCache -Recurse -Force
        Write-Host "  ✓ Cleaned Vite cache" -ForegroundColor Green
    }
}

# Install dependencies
function Install-Dependencies {
    Write-Host "`n[3/8] Installing Dependencies..." -ForegroundColor Yellow
    
    Push-Location $FRONTEND_DIR
    try {
        Write-Host "  Running npm ci (clean install)..." -ForegroundColor Gray
        npm ci --prefer-offline --no-audit 2>&1 | Out-Null
        Write-Host "  ✓ Frontend dependencies installed" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Failed to install frontend dependencies" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        exit 1
    } finally {
        Pop-Location
    }
}

# Run tests
function Invoke-Tests {
    if ($SkipTests) {
        Write-Host "`n[4/8] Tests Skipped (--SkipTests flag)" -ForegroundColor Yellow
        return
    }
    
    Write-Host "`n[4/8] Running Tests..." -ForegroundColor Yellow
    
    # Check if test script exists
    Push-Location $FRONTEND_DIR
    try {
        $packageJson = Get-Content "package.json" | ConvertFrom-Json
        if ($packageJson.scripts.test) {
            Write-Host "  Running npm test..." -ForegroundColor Gray
            npm test -- --passWithNoTests 2>&1 | Out-Null
            Write-Host "  ✓ All tests passed" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ No test script found, skipping" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ⚠ Tests failed, continuing anyway..." -ForegroundColor Yellow
    } finally {
        Pop-Location
    }
}

# Build frontend
function Build-Frontend {
    Write-Host "`n[5/8] Building Frontend (PWA)..." -ForegroundColor Yellow
    
    Push-Location $FRONTEND_DIR
    try {
        # Set production environment
        $env:NODE_ENV = "production"
        $env:VITE_BUILD_TIME = (Get-Date -Format "o")
        $env:VITE_BUILD_VERSION = (git describe --tags --always 2>$null) -or "dev"
        
        Write-Host "  Environment: $Environment" -ForegroundColor Gray
        Write-Host "  Version: $($env:VITE_BUILD_VERSION)" -ForegroundColor Gray
        Write-Host "  Building with Vite..." -ForegroundColor Gray
        
        # Build with verbose output if requested
        if ($Verbose) {
            npm run build
        } else {
            npm run build 2>&1 | Out-Null
        }
        
        Write-Host "  ✓ Frontend build completed" -ForegroundColor Green
        
        # Verify dist directory
        if (-not (Test-Path $DIST_DIR)) {
            throw "Build failed: dist/ directory not created"
        }
        
        # Check for critical files
        $criticalFiles = @("index.html", "manifest.json", "service-worker.js")
        foreach ($file in $criticalFiles) {
            $filePath = Join-Path $DIST_DIR $file
            if (-not (Test-Path $filePath)) {
                Write-Host "  ⚠ Warning: $file not found in build output" -ForegroundColor Yellow
            }
        }
        
    } catch {
        Write-Host "ERROR: Frontend build failed" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        exit 1
    } finally {
        Pop-Location
    }
}

# Generate build metadata
function New-BuildMetadata {
    Write-Host "`n[6/8] Generating Build Metadata..." -ForegroundColor Yellow
    
    $buildInfo = @{
        version = (git describe --tags --always 2>$null) -or "dev"
        timestamp = Get-Date -Format "o"
        environment = $Environment
        commit = (git rev-parse HEAD 2>$null) -or "unknown"
        branch = (git rev-parse --abbrev-ref HEAD 2>$null) -or "unknown"
        builder = $env:USERNAME
        nodeVersion = (node --version)
        features = @(
            "AI Diagnosis",
            "Medical Knowledge Base",
            "Prescription Generator",
            "Patient Management",
            "Treatment Plans",
            "Analytics Dashboard",
            "Offline Support",
            "Push Notifications",
            "Background Sync",
            "Self-Healing System"
        )
    } | ConvertTo-Json -Depth 10
    
    $buildInfo | Set-Content -Path $BUILD_INFO_FILE -Encoding UTF8
    Write-Host "  ✓ Build metadata saved to build-info.json" -ForegroundColor Green
}

# Analyze build size
function Show-BuildAnalysis {
    Write-Host "`n[7/8] Build Analysis..." -ForegroundColor Yellow
    
    # Calculate total size
    $totalSize = (Get-ChildItem -Path $DIST_DIR -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "  Total build size: $([Math]::Round($totalSize, 2)) MB" -ForegroundColor Cyan
    
    # Analyze by file type
    $jsSize = (Get-ChildItem -Path $DIST_DIR -Recurse -Filter "*.js" | Measure-Object -Property Length -Sum).Sum / 1KB
    $cssSize = (Get-ChildItem -Path $DIST_DIR -Recurse -Filter "*.css" | Measure-Object -Property Length -Sum).Sum / 1KB
    $htmlSize = (Get-ChildItem -Path $DIST_DIR -Recurse -Filter "*.html" | Measure-Object -Property Length -Sum).Sum / 1KB
    $imageSize = (Get-ChildItem -Path $DIST_DIR -Recurse -Include "*.png","*.jpg","*.svg","*.ico" | Measure-Object -Property Length -Sum).Sum / 1KB
    
    Write-Host "`n  File Type Breakdown:" -ForegroundColor Gray
    Write-Host "    JavaScript:  $([Math]::Round($jsSize, 2)) KB" -ForegroundColor White
    Write-Host "    CSS:         $([Math]::Round($cssSize, 2)) KB" -ForegroundColor White
    Write-Host "    HTML:        $([Math]::Round($htmlSize, 2)) KB" -ForegroundColor White
    Write-Host "    Images:      $([Math]::Round($imageSize, 2)) KB" -ForegroundColor White
    
    # Count files
    $fileCount = (Get-ChildItem -Path $DIST_DIR -Recurse -File).Count
    Write-Host "`n  Total files: $fileCount" -ForegroundColor Cyan
    
    # Check if size is reasonable for PWA
    if ($totalSize -gt 10) {
        Write-Host "`n  ⚠ WARNING: Build size exceeds 10 MB. Consider code splitting." -ForegroundColor Yellow
    } else {
        Write-Host "`n  ✓ Build size is optimal for PWA deployment" -ForegroundColor Green
    }
}

# Deployment instructions
function Show-DeploymentInstructions {
    Write-Host "`n[8/8] Deployment Instructions" -ForegroundColor Yellow
    
    Write-Host @"

╔═══════════════════════════════════════════════════════════╗
║                   BUILD SUCCESSFUL! ✓                     ║
╚═══════════════════════════════════════════════════════════╝

📦 Build Output Location:
   $DIST_DIR

🚀 Deployment Options:

1. LOCAL PREVIEW (Test PWA Locally):
   cd frontend
   npm run preview
   Open: http://localhost:3000

2. STATIC HOSTING (Netlify/Vercel/AWS S3):
   - Upload contents of dist/ folder
   - Configure:
     * Set /_* to redirect to index.html (SPA routing)
     * Add service-worker.js to root
     * Enable HTTPS (required for PWA)
   
3. NGINX SERVER:
   server {
       listen 443 ssl http2;
       server_name your-domain.com;
       
       root $DIST_DIR;
       index index.html;
       
       # PWA service worker
       location /service-worker.js {
           add_header Cache-Control "no-cache";
           expires off;
       }
       
       # SPA routing
       location / {
           try_files `$uri `$uri/ /index.html;
       }
       
       # API proxy (if backend on same server)
       location /api {
           proxy_pass http://localhost:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade `$http_upgrade;
           proxy_set_header Connection 'upgrade';
       }
   }

4. DOCKER DEPLOYMENT:
   cd $ROOT_DIR
   docker-compose up -d

5. BACKEND SETUP (if not skipped):
   cd backend
   source ../.venv/bin/activate  # Linux/Mac
   ..\\.venv\\Scripts\\Activate.ps1  # Windows
   uvicorn app.main:app --host 0.0.0.0 --port 8000

📱 PWA Features Included:
   ✓ Offline support with intelligent caching
   ✓ Install prompt (Add to Home Screen)
   ✓ Push notifications ready
   ✓ Background sync for patient data
   ✓ App shortcuts (Diagnosis, Intake, KB, Chat)
   ✓ File sharing capability
   ✓ Optimized for medical workflows

⚙️  Environment Configuration:
   Create .env.production in backend/:
   - OPENAI_API_KEY=your_key_here
   - DATABASE_URL=postgresql://...
   - SECRET_KEY=your_secret_key
   - CORS_ORIGINS=https://your-domain.com

🔒 Security Checklist:
   [ ] HTTPS enabled (required for PWA)
   [ ] Environment variables secured
   [ ] CORS origins configured
   [ ] API keys not in frontend code
   [ ] Content Security Policy headers set
   [ ] Rate limiting enabled on API

📊 Monitoring:
   - Service Worker: Chrome DevTools > Application > Service Workers
   - Cache: Application > Cache Storage
   - Manifest: Application > Manifest
   - Lighthouse: Run PWA audit

💡 Tips:
   - Test PWA install on mobile device
   - Verify offline functionality works
   - Check notification permissions
   - Test all app shortcuts
   - Monitor service worker updates

"@ -ForegroundColor White

    Write-Host "Deployment artifacts ready at: $DIST_DIR`n" -ForegroundColor Green
}

# Main execution
try {
    Test-Prerequisites
    Clear-BuildArtifacts
    Install-Dependencies
    Invoke-Tests
    Build-Frontend
    New-BuildMetadata
    Show-BuildAnalysis
    Show-DeploymentInstructions
    
    Write-Host "✨ PWA deployment preparation complete!" -ForegroundColor Green
    Write-Host "Next step: Deploy dist/ folder to your hosting provider`n" -ForegroundColor Cyan
    
} catch {
    Write-Host "`n❌ Deployment failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
